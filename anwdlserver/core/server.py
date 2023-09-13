"""
	Copyright 2023 The Anweddol project
	See the LICENSE file for licensing informations
	---

	Main server functionalities

"""
from typing import Callable
import threading
import traceback
import socket
import time


# Intern importation
from .virtualization import VirtualizationInterface
from .port_forwarding import PortForwardingInterface
from .database import DatabaseInterface
from .client import ClientInstance
from .utilities import isSocketClosed
from .crypto import RSAWrapper

# Version indicator importation
from ..__init__ import __version__

# Default parameters
DEFAULT_SERVER_BIND_ADDRESS = ""
DEFAULT_SERVER_LISTEN_PORT = 6150
DEFAULT_CLIENT_TIMEOUT = 10

DEFAULT_DIE_ON_ERROR = False

# Constants definition
REQUEST_VERB_CREATE = "CREATE"
REQUEST_VERB_DESTROY = "DESTROY"
REQUEST_VERB_STAT = "STAT"

RESPONSE_MSG_OK = "OK"
RESPONSE_MSG_BAD_AUTH = "Bad authentication"
RESPONSE_MSG_BAD_REQ = "Bad request"
RESPONSE_MSG_REFUSED_REQ = "Refused request"
RESPONSE_MSG_UNAVAILABLE = "Unavailable"
RESPONSE_MSG_UNSPECIFIED = "Unspecified"
RESPONSE_MSG_INTERNAL_ERROR = "Internal error"

EVENT_CONTAINER_CREATED = "on_container_created"
EVENT_CONTAINER_DOMAIN_STARTED = "on_container_domain_started"
EVENT_CONTAINER_DOMAIN_STOPPED = "on_container_domain_stopped"
EVENT_FORWARDER_CREATED = "on_forwarder_created"
EVENT_FORWARDER_STARTED = "on_forwarder_started"
EVENT_FORWARDER_STOPPED = "on_forwarder_stopped"
EVENT_ENDPOINT_SHELL_CREATED = "on_endpoint_shell_created"
EVENT_ENDPOINT_SHELL_OPENED = "on_endpoint_shell_opened"
EVENT_ENDPOINT_SHELL_CLOSED = "on_endpoint_shell_closed"
EVENT_SERVER_STARTED = "on_server_started"
EVENT_SERVER_STOPPED = "on_server_stopped"
EVENT_CLIENT_INITIALIZED = "on_client_initialized"
EVENT_CLIENT_CLOSED = "on_client_closed"
EVENT_CONNECTION_ACCEPTED = "on_connection_accepted"
EVENT_REQUEST = "on_request"
EVENT_AUTHENTICATION_ERROR = "on_authentication_error"
EVENT_RUNTIME_ERROR = "on_runtime_error"
EVENT_MALFORMED_REQUEST = "on_malformed_request"
EVENT_UNHANDLED_VERB = "on_unhandled_verb"

CONTEXT_NORMAL_PROCESS = 20
CONTEXT_AUTOMATIC_ACTION = 21
CONTEXT_HANDLE_END = 22
CONTEXT_ERROR = 23


class ServerInterface:
    def __init__(
        self,
        runtime_container_iso_file_path: str,
        bind_address: str = DEFAULT_SERVER_BIND_ADDRESS,
        listen_port: int = DEFAULT_SERVER_LISTEN_PORT,
        client_timeout: int | None = DEFAULT_CLIENT_TIMEOUT,
        runtime_virtualization_interface: VirtualizationInterface = None,
        runtime_database_interface: DatabaseInterface = None,
        runtime_port_forwarding_interface: PortForwardingInterface = None,
        runtime_rsa_wrapper: RSAWrapper = None,
    ):
        self.request_handler_dict = {
            REQUEST_VERB_CREATE: self.__handle_create_request,
            REQUEST_VERB_DESTROY: self.__handle_destroy_request,
            REQUEST_VERB_STAT: self.__handle_stat_request,
        }

        self.event_handler_dict = {
            EVENT_CONTAINER_CREATED: None,
            EVENT_CONTAINER_DOMAIN_STARTED: None,
            EVENT_CONTAINER_DOMAIN_STOPPED: None,
            EVENT_FORWARDER_CREATED: None,
            EVENT_FORWARDER_STARTED: None,
            EVENT_FORWARDER_STOPPED: None,
            EVENT_ENDPOINT_SHELL_CREATED: None,
            EVENT_ENDPOINT_SHELL_OPENED: None,
            EVENT_ENDPOINT_SHELL_CLOSED: None,
            EVENT_SERVER_STARTED: None,
            EVENT_SERVER_STOPPED: None,
            EVENT_CLIENT_INITIALIZED: None,
            EVENT_CLIENT_CLOSED: None,
            EVENT_CONNECTION_ACCEPTED: None,
            EVENT_REQUEST: None,
            EVENT_AUTHENTICATION_ERROR: None,
            EVENT_RUNTIME_ERROR: None,
            EVENT_MALFORMED_REQUEST: None,
            EVENT_UNHANDLED_VERB: None,
        }

        self.server_sock = None
        self.listen_port = listen_port
        self.bind_address = bind_address
        self.client_timeout = client_timeout
        self.container_iso_file_path = runtime_container_iso_file_path

        self.recorded_runtime_errors_counter = 0
        self.start_timestamp = None
        self.is_running = False

        self.virtualization_interface = (
            runtime_virtualization_interface
            if runtime_virtualization_interface
            else VirtualizationInterface()
        )
        self.database_interface = (
            runtime_database_interface
            if runtime_database_interface
            else DatabaseInterface()
        )
        self.port_forwarding_interface = (
            runtime_port_forwarding_interface
            if runtime_port_forwarding_interface
            else PortForwardingInterface()
        )
        self.rsa_wrapper = runtime_rsa_wrapper if runtime_rsa_wrapper else RSAWrapper()

    def __del__(self):
        if self.is_running:
            self.__stop_server()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        if self.is_running:
            self.__stop_server()

    def __format_traceback(self, exception):
        return "".join(
            traceback.format_exception(
                type(exception), exception, exception.__traceback__
            )
        )

    def __execute_event_handler(self, event, context, data={}):
        if event == EVENT_RUNTIME_ERROR:
            self.recorded_runtime_errors_counter += 1

        if self.event_handler_dict.get(event):
            self.event_handler_dict[event](context=context, data=data)

        if data.get("client_instance") and data.get("client_instance").isClosed():
            return -1

    def __store_container(self, container_instance, forwarder_instance):
        _, _, new_client_token = self.database_interface.addEntry(
            container_instance.getUUID()
        )
        self.virtualization_interface.storeContainer(container_instance)
        self.port_forwarding_interface.storeForwarder(forwarder_instance)

        return new_client_token

    def __delete_container(self, container_instance):
        self.database_interface.deleteEntry(
            self.database_interface.getContainerUUIDEntryID(
                container_instance.getUUID()
            )
        )
        self.virtualization_interface.deleteStoredContainer(
            container_instance.getUUID()
        )
        self.port_forwarding_interface.deleteStoredForwarder(container_instance.getIP())

    # This routine detects inactive container and destroy them in consequence
    def __delete_container_on_domain_shutdown_routine(self):
        while self.is_running:
            try:
                # Container UUID to delete are stored in a list and deleted after the
                # first loop to avoid the "Dictionary changed size during iteration" error
                container_instance_list = []

                for (
                    container_uuid
                ) in self.virtualization_interface.listStoredContainers():
                    container_instance = (
                        self.virtualization_interface.getStoredContainer(container_uuid)
                    )

                    if not container_instance.isDomainRunning():
                        container_instance_list.append(container_instance)

                for container_instance in container_instance_list:
                    forwarder_instance = (
                        self.port_forwarding_interface.getStoredForwarder(
                            container_instance.getIP()
                        )
                    )

                    if forwarder_instance and forwarder_instance.isForwarding():
                        forwarder_instance.stopForward()

                        self.__execute_event_handler(
                            EVENT_FORWARDER_STOPPED,
                            CONTEXT_AUTOMATIC_ACTION,
                            data={"forwarder_instance": forwarder_instance},
                        )

                    self.__delete_container(container_instance)

                    # Mark the container instance domain as stopped
                    self.__execute_event_handler(
                        EVENT_CONTAINER_DOMAIN_STOPPED,
                        CONTEXT_AUTOMATIC_ACTION,
                        data={"container_instance": container_instance},
                    )

            except Exception as E:
                self.__execute_event_handler(
                    EVENT_RUNTIME_ERROR,
                    CONTEXT_ERROR,
                    data={
                        "exception_object": E,
                        "traceback": self.__format_traceback(E),
                    },
                )

            time.sleep(1)

    def __start_server(self):
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_sock.bind((self.bind_address, self.listen_port))
        self.server_sock.listen(5)

        self.start_timestamp = int(time.time())
        self.is_running = True

        threading.Thread(
            target=self.__delete_container_on_domain_shutdown_routine
        ).start()

        self.__execute_event_handler(EVENT_SERVER_STARTED, CONTEXT_NORMAL_PROCESS)

        self.__main_server_loop_routine()

    def __stop_server(self, raise_errors=False, die_on_error=False):
        try:
            # Container UUID to delete are stored in a list and deleted after the
            # first loop to avoid the "Dictionary changed size during iteration" error
            container_instance_list = []

            for container_uuid in self.virtualization_interface.listStoredContainers():
                container_instance_list.append(
                    self.virtualization_interface.getStoredContainer(container_uuid)
                )

            for container_instance in container_instance_list:
                # Just a failsafe condition
                if container_instance.isDomainRunning():
                    container_instance.stopDomain()

                    self.__execute_event_handler(
                        EVENT_CONTAINER_DOMAIN_STOPPED,
                        CONTEXT_NORMAL_PROCESS,
                        data={"container_instance": container_instance},
                    )

                self.__delete_container(container_instance)

            self.database_interface.closeDatabase()
            self.server_sock.close()

            self.is_running = False

            self.__execute_event_handler(EVENT_SERVER_STOPPED, CONTEXT_NORMAL_PROCESS)

        except Exception as E:
            if raise_errors:
                raise E

            self.__execute_event_handler(
                EVENT_RUNTIME_ERROR,
                CONTEXT_ERROR,
                data={
                    "exception_object": E,
                    "traceback": self.__format_traceback(E),
                },
            )

            if die_on_error:
                exit(0xDEAD)

    # Intern methods for normal processes
    def __handle_create_request(self, client_instance):
        new_endpoint_shell_instance = None
        new_container_instance = None
        new_forwarder_instance = None

        try:
            # Create and start the container domain
            new_container_instance = self.virtualization_interface.createContainer(
                store=False
            )
            new_container_instance.setISOFilePath(self.container_iso_file_path)

            if (
                self.__execute_event_handler(
                    EVENT_CONTAINER_CREATED,
                    CONTEXT_NORMAL_PROCESS,
                    data={
                        "client_instance": client_instance,
                        "container_instance": new_container_instance,
                    },
                )
                == -1
            ):
                return

            if not new_container_instance.isDomainRunning():
                new_container_instance.startDomain()

                if (
                    self.__execute_event_handler(
                        EVENT_CONTAINER_DOMAIN_STARTED,
                        CONTEXT_NORMAL_PROCESS,
                        data={
                            "client_instance": client_instance,
                            "container_instance": new_container_instance,
                        },
                    )
                    == -1
                ):
                    return

            # Create an endpoint shell on the container and administrate it
            new_endpoint_shell_instance = new_container_instance.createEndpointShell(
                open_shell=False
            )

            if (
                self.__execute_event_handler(
                    EVENT_ENDPOINT_SHELL_CREATED,
                    CONTEXT_NORMAL_PROCESS,
                    data={
                        "client_instance": client_instance,
                        "endpoint_shell_instance": new_endpoint_shell_instance,
                    },
                )
                == -1
            ):
                return

            new_container_username, new_container_password = (
                new_endpoint_shell_instance.generateClientSSHCredentials()
                if not all(
                    list(new_endpoint_shell_instance.getStoredClientSSHCredentials())
                )
                else new_endpoint_shell_instance.getStoredClientSSHCredentials()
            )

            if new_endpoint_shell_instance.isClosed():
                new_endpoint_shell_instance.openShell()

                if (
                    self.__execute_event_handler(
                        EVENT_ENDPOINT_SHELL_OPENED,
                        CONTEXT_NORMAL_PROCESS,
                        data={
                            "client_instance": client_instance,
                            "endpoint_shell_instance": new_endpoint_shell_instance,
                        },
                    )
                    == -1
                ):
                    return

            if not new_endpoint_shell_instance.isClosed():
                new_endpoint_shell_instance.administrateContainer()
                new_endpoint_shell_instance.closeShell()

                if (
                    self.__execute_event_handler(
                        EVENT_ENDPOINT_SHELL_CLOSED,
                        CONTEXT_NORMAL_PROCESS,
                        data={
                            "client_instance": client_instance,
                            "endpoint_shell_instance": new_endpoint_shell_instance,
                        },
                    )
                    == -1
                ):
                    return

            # Create a new forwarder and start it
            new_forwarder_instance = self.port_forwarding_interface.createForwarder(
                new_container_instance.getIP(), 22, store=False
            )

            if (
                self.__execute_event_handler(
                    EVENT_FORWARDER_CREATED,
                    CONTEXT_NORMAL_PROCESS,
                    data={
                        "client_instance": client_instance,
                        "forwarder_instance": new_forwarder_instance,
                    },
                )
                == -1
            ):
                return

            if not new_forwarder_instance.isForwarding():
                new_forwarder_instance.startForward()

                if (
                    self.__execute_event_handler(
                        EVENT_FORWARDER_STARTED,
                        CONTEXT_NORMAL_PROCESS,
                        data={
                            "client_instance": client_instance,
                            "forwarder_instance": new_forwarder_instance,
                        },
                    )
                    == -1
                ):
                    return

            # Store new container environment informations
            new_client_token = self.__store_container(
                new_container_instance, new_forwarder_instance
            )

            if not client_instance.isClosed():
                client_instance.sendResponse(
                    True,
                    RESPONSE_MSG_OK,
                    data={
                        "container_uuid": new_container_instance.getUUID(),
                        "client_token": new_client_token,
                        "container_iso_sha256": new_container_instance.makeISOFileChecksum(),
                        "container_username": new_container_username,
                        "container_password": new_container_password,
                        "container_listen_port": new_forwarder_instance.getServerOriginPort(),
                    },
                )

        except Exception as E:
            if (
                self.__execute_event_handler(
                    EVENT_RUNTIME_ERROR,
                    CONTEXT_ERROR,
                    data={
                        "exception_object": E,
                        "traceback": self.__format_traceback(E),
                        "client_instance": client_instance,
                    },
                )
                == -1
            ):
                return

            # Chech if the error is due to a broken pipe caused by peer,
            # no response will be sent if it is the case
            if not client_instance.isClosed() and "Peer refused the packet" not in str(
                E
            ):
                client_instance.sendResponse(False, RESPONSE_MSG_INTERNAL_ERROR)

            if new_forwarder_instance and new_forwarder_instance.isForwarding():
                new_forwarder_instance.stopForward()

                if (
                    self.__execute_event_handler(
                        EVENT_FORWARDER_STOPPED,
                        CONTEXT_ERROR,
                        data={
                            "client_instance": client_instance,
                            "forwarder_instance": new_forwarder_instance,
                        },
                    )
                    == -1
                ):
                    return

            if new_endpoint_shell_instance and new_endpoint_shell_instance.isClosed():
                new_endpoint_shell_instance.closeShell()

                if (
                    self.__execute_event_handler(
                        EVENT_ENDPOINT_SHELL_CLOSED,
                        CONTEXT_ERROR,
                        data={
                            "client_instance": client_instance,
                            "endpoint_shell_instance": new_endpoint_shell_instance,
                        },
                    )
                    == -1
                ):
                    return

            if new_container_instance and new_container_instance.isDomainRunning():
                new_container_instance.stopDomain()

                if (
                    self.__execute_event_handler(
                        EVENT_CONTAINER_DOMAIN_STOPPED,
                        CONTEXT_ERROR,
                        data={
                            "client_instance": client_instance,
                            "container_instance": new_container_instance,
                        },
                    )
                    == -1
                ):
                    return

            if new_container_instance:
                self.__delete_container(new_container_instance)

    def __handle_destroy_request(self, client_instance):
        stored_request = client_instance.getStoredRequest()

        if not self.database_interface.getEntryID(
            stored_request["parameters"].get("container_uuid"),
            stored_request["parameters"].get("client_token"),
        ):
            self.__execute_event_handler(
                EVENT_AUTHENTICATION_ERROR,
                CONTEXT_ERROR,
                data={"client_instance": client_instance},
            )

            if not client_instance.isClosed():
                client_instance.sendResponse(False, RESPONSE_MSG_BAD_AUTH)

            return

        container_instance = self.virtualization_interface.getStoredContainer(
            stored_request["parameters"].get("container_uuid")
        )

        if container_instance.isDomainRunning():
            container_instance.stopDomain()

            if (
                self.__execute_event_handler(
                    EVENT_CONTAINER_DOMAIN_STOPPED,
                    CONTEXT_NORMAL_PROCESS,
                    data={
                        "client_instance": client_instance,
                        "container_instance": container_instance,
                    },
                )
                == -1
            ):
                return

        forwarder_instance = self.port_forwarding_interface.getStoredForwarder(
            container_instance.getIP()
        )

        if forwarder_instance and forwarder_instance.isForwarding():
            forwarder_instance.stopForward()

            if (
                self.__execute_event_handler(
                    EVENT_FORWARDER_STOPPED,
                    CONTEXT_NORMAL_PROCESS,
                    data={
                        "client_instance": client_instance,
                        "forwarder_instance": forwarder_instance,
                    },
                )
                == -1
            ):
                return

        self.__delete_container(container_instance)

        client_instance.sendResponse(True, RESPONSE_MSG_OK)

    def __handle_stat_request(self, client_instance):
        client_instance.sendResponse(
            True,
            RESPONSE_MSG_OK,
            data={
                "version": __version__,
                "uptime": int(time.time()) - self.start_timestamp,
            },
        )

    def __handle_new_client(self, client_instance):
        try:
            (
                is_recv_request_conform,
                recv_request_content,
                _,
            ) = client_instance.recvRequest()

            if not is_recv_request_conform:
                self.__execute_event_handler(
                    EVENT_MALFORMED_REQUEST,
                    CONTEXT_ERROR,
                    data={"client_instance": client_instance},
                )

                if not client_instance.isClosed():
                    client_instance.sendResponse(
                        False,
                        RESPONSE_MSG_BAD_REQ,
                        reason="Malformed request",
                    )

                    client_instance.closeConnection()

                    self.__execute_event_handler(
                        EVENT_CLIENT_CLOSED,
                        CONTEXT_HANDLE_END,
                        data={"client_instance": client_instance},
                    )

                return

            if not self.request_handler_dict.get(recv_request_content["verb"]):
                self.__execute_event_handler(
                    EVENT_UNHANDLED_VERB,
                    CONTEXT_ERROR,
                    data={"client_instance": client_instance},
                )

                if not client_instance.isClosed():
                    client_instance.sendResponse(
                        False,
                        RESPONSE_MSG_BAD_REQ,
                        reason="Unhandled verb",
                    )

                    client_instance.closeConnection()

                    self.__execute_event_handler(
                        EVENT_CLIENT_CLOSED,
                        CONTEXT_HANDLE_END,
                        data={"client_instance": client_instance},
                    )

                return

            if (
                self.__execute_event_handler(
                    EVENT_REQUEST,
                    CONTEXT_NORMAL_PROCESS,
                    data={"client_instance": client_instance},
                )
                == -1
            ):
                return

            if client_instance.isClosed():
                return

            # Request handler execution
            self.request_handler_dict[recv_request_content["verb"]](
                client_instance=client_instance
            )

            if not client_instance.isClosed():
                client_instance.closeConnection()

                self.__execute_event_handler(
                    EVENT_CLIENT_CLOSED,
                    CONTEXT_HANDLE_END,
                    data={"client_instance": client_instance},
                )

        except Exception as E:
            self.__execute_event_handler(
                EVENT_RUNTIME_ERROR,
                CONTEXT_ERROR,
                data={
                    "exception_object": E,
                    "traceback": self.__format_traceback(E),
                    "client_instance": client_instance,
                },
            )

            if not client_instance.isClosed():
                client_instance.sendResponse(
                    False,
                    RESPONSE_MSG_INTERNAL_ERROR,
                )

                client_instance.closeConnection()

                self.__execute_event_handler(
                    EVENT_CLIENT_CLOSED,
                    CONTEXT_HANDLE_END,
                    data={"client_instance": client_instance},
                )

    def __main_server_loop_routine(self):
        while self.is_running:
            new_client_instance = None

            try:
                try:
                    new_client_socket, _ = self.server_sock.accept()

                except OSError:
                    # If the server socket is closed in an external method,
                    # will raise OSError here
                    break

                if (
                    self.__execute_event_handler(
                        EVENT_CONNECTION_ACCEPTED,
                        CONTEXT_NORMAL_PROCESS,
                        data={"client_socket": new_client_socket},
                    )
                    == -1
                ):
                    return

                if isSocketClosed(new_client_socket):
                    continue

                new_client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

                if self.client_timeout:
                    new_client_socket.settimeout(self.client_timeout)

                new_client_instance = ClientInstance(
                    new_client_socket,
                    rsa_wrapper=self.rsa_wrapper,
                )

                if (
                    self.__execute_event_handler(
                        EVENT_CLIENT_INITIALIZED,
                        CONTEXT_NORMAL_PROCESS,
                        data={"client_instance": new_client_instance},
                    )
                    == -1
                ):
                    return

                if new_client_instance.isClosed():
                    continue

                threading.Thread(
                    target=self.__handle_new_client, args=[new_client_instance]
                ).start()

            except Exception as E:
                data = {
                    "exception_object": E,
                    "traceback": self.__format_traceback(E),
                    "client_socket": new_client_socket,
                }

                if new_client_instance:
                    data.update({"client_instance": new_client_instance})

                self.__execute_event_handler(
                    EVENT_RUNTIME_ERROR, CONTEXT_ERROR, data=data
                )

                if new_client_instance and not new_client_instance.isClosed():
                    new_client_instance.sendResponse(False, RESPONSE_MSG_INTERNAL_ERROR)

                    new_client_instance.closeConnection()

                    self.__execute_event_handler(
                        EVENT_CLIENT_CLOSED,
                        CONTEXT_HANDLE_END,
                        data={"client_instance": new_client_instance},
                    )

                if not isSocketClosed(new_client_socket):
                    new_client_socket.close()

    # Event decorators binding for event callback
    @property
    def on_container_created(self):
        def wrapper(routine):
            self.event_handler_dict.update({EVENT_CONTAINER_CREATED: routine})
            return wrapper

        return wrapper

    @property
    def on_container_domain_started(self):
        def wrapper(routine):
            self.event_handler_dict.update({EVENT_CONTAINER_DOMAIN_STARTED: routine})
            return wrapper

        return wrapper

    @property
    def on_container_domain_stopped(self):
        def wrapper(routine):
            self.event_handler_dict.update({EVENT_CONTAINER_DOMAIN_STOPPED: routine})
            return wrapper

        return wrapper

    @property
    def on_forwarder_created(self):
        def wrapper(routine):
            self.event_handler_dict.update({EVENT_FORWARDER_CREATED: routine})
            return wrapper

        return wrapper

    @property
    def on_forwarder_started(self):
        def wrapper(routine):
            self.event_handler_dict.update({EVENT_FORWARDER_STARTED: routine})
            return wrapper

        return wrapper

    @property
    def on_forwarder_stopped(self):
        def wrapper(routine):
            self.event_handler_dict.update({EVENT_FORWARDER_STOPPED: routine})
            return wrapper

        return wrapper

    @property
    def on_endpoint_shell_created(self):
        def wrapper(routine):
            self.event_handler_dict.update({EVENT_ENDPOINT_SHELL_CREATED: routine})
            return wrapper

        return wrapper

    @property
    def on_endpoint_shell_opened(self):
        def wrapper(routine):
            self.event_handler_dict.update({EVENT_ENDPOINT_SHELL_OPENED: routine})
            return wrapper

        return wrapper

    @property
    def on_endpoint_shell_closed(self):
        def wrapper(routine):
            self.event_handler_dict.update({EVENT_ENDPOINT_SHELL_CLOSED: routine})
            return wrapper

        return wrapper

    @property
    def on_server_started(self):
        def wrapper(routine):
            self.event_handler_dict.update({EVENT_SERVER_STARTED: routine})
            return wrapper

        return wrapper

    @property
    def on_server_stopped(self):
        def wrapper(routine):
            self.event_handler_dict.update({EVENT_SERVER_STOPPED: routine})
            return wrapper

        return wrapper

    @property
    def on_client_initialized(self):
        def wrapper(routine):
            self.event_handler_dict.update({EVENT_CLIENT_INITIALIZED: routine})
            return wrapper

        return wrapper

    @property
    def on_client_closed(self):
        def wrapper(routine):
            self.event_handler_dict.update({EVENT_CLIENT_CLOSED: routine})
            return wrapper

        return wrapper

    @property
    def on_connection_accepted(self):
        def wrapper(routine):
            self.event_handler_dict.update({EVENT_CONNECTION_ACCEPTED: routine})
            return wrapper

        return wrapper

    @property
    def on_request(self):
        def wrapper(routine):
            self.event_handler_dict.update({EVENT_REQUEST: routine})
            return wrapper

        return wrapper

    @property
    def on_authentication_error(self):
        def wrapper(routine):
            self.event_handler_dict.update({EVENT_AUTHENTICATION_ERROR: routine})
            return wrapper

        return wrapper

    @property
    def on_runtime_error(self):
        def wrapper(routine):
            self.event_handler_dict.update({EVENT_RUNTIME_ERROR: routine})
            return wrapper

        return wrapper

    @property
    def on_malformed_request(self):
        def wrapper(routine):
            self.event_handler_dict.update({EVENT_MALFORMED_REQUEST: routine})
            return wrapper

        return wrapper

    @property
    def on_unhandled_verb(self):
        def wrapper(routine):
            self.event_handler_dict.update({EVENT_UNHANDLED_VERB: routine})
            return wrapper

        return wrapper

    # Utility methods
    def getRuntimeContainerISOFilePath(self) -> str:
        return self.runtime_container_iso_file_path

    def getRuntimeDatabaseInterface(self) -> DatabaseInterface:
        return self.database_interface

    def getRuntimeVirtualizationInterface(self) -> VirtualizationInterface:
        return self.virtualization_interface

    def getRuntimeRSAWrapper(self) -> RSAWrapper:
        return self.rsa_wrapper

    def getRuntimePortForwardingInterface(self) -> PortForwardingInterface:
        return self.port_forwarding_interface

    def getRuntimeStatistics(self) -> tuple:
        return (
            self.is_running,
            self.recorded_runtime_errors_counter,
            int(time.time()) - self.start_timestamp,
        )

    def getRequestHandler(self, verb: str) -> None | Callable:
        return self.request_handler_dict.get(verb)

    def getEventHandler(self, event: int) -> None | Callable:
        return self.event_handler_dict.get(event)

    def setRuntimeContainerISOFilePath(self, iso_file_path: str) -> None:
        self.runtime_container_iso_file_path = iso_file_path

    def setRuntimeDatabaseInterface(
        self, database_interface: DatabaseInterface
    ) -> None:
        self.database_interface = database_interface

    def setRuntimeVirtualizationInterface(
        self, virtualization_interface: VirtualizationInterface
    ) -> None:
        self.virtualization_interface = virtualization_interface

    def setRuntimeRSAWrapper(self, rsa_wrapper: RSAWrapper) -> None:
        self.runtime_rsa_wrapper = rsa_wrapper

    def setRuntimePortForwardingInterface(
        self, port_forwarding_interface: PortForwardingInterface
    ) -> None:
        self.port_forwarding_interface = port_forwarding_interface

    def setRequestHandler(self, verb: str, routine: Callable) -> None:
        self.request_handler_dict.update({verb: routine})

    def setEventHandler(self, event: int, routine: Callable) -> None:
        self.event_handler_dict.update({event: routine})

    def startServer(self) -> None:
        if self.is_running:
            raise RuntimeError("Server is already running")

        self.__start_server()

    def stopServer(self, die_on_error: bool = DEFAULT_DIE_ON_ERROR) -> None:
        if not self.is_running:
            if die_on_error:
                return

            raise RuntimeError("Server is already stopped")

        self.__stop_server(raise_errors=True, die_on_error=die_on_error)
