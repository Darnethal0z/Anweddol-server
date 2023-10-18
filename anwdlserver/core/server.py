"""
Copyright 2023 The Anweddol project
See the LICENSE file for licensing informations
---

This module is the main Anweddol server process.
In connects every other core modules into a single one
so that they can all be used in a single module.

"""

from typing import Callable, Any, Union
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
from .sanitization import makeResponse

# Version indicator importation
from ..__init__ import __version__

# Default parameters
DEFAULT_SERVER_BIND_ADDRESS = ""
DEFAULT_SERVER_LISTEN_PORT = 6150
DEFAULT_CLIENT_TIMEOUT = 10

DEFAULT_DIE_ON_ERROR = False
DEFAULT_PASSIVE_MODE = False

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
CONTEXT_DEFERRED_CALL = 22
CONTEXT_HANDLE_END = 23
CONTEXT_ERROR = 24


class ServerInterface:
    def __init__(
        self,
        runtime_container_iso_file_path: str,
        bind_address: str = DEFAULT_SERVER_BIND_ADDRESS,
        listen_port: int = DEFAULT_SERVER_LISTEN_PORT,
        client_timeout: Union[int, None] = DEFAULT_CLIENT_TIMEOUT,
        runtime_virtualization_interface: VirtualizationInterface = None,
        runtime_database_interface: DatabaseInterface = None,
        runtime_port_forwarding_interface: PortForwardingInterface = None,
        runtime_rsa_wrapper: RSAWrapper = None,
        passive_mode: bool = DEFAULT_PASSIVE_MODE,
    ):
        self.request_handler_dict = {
            REQUEST_VERB_CREATE: self._handle_create_request,
            REQUEST_VERB_DESTROY: self._handle_destroy_request,
            REQUEST_VERB_STAT: self._handle_stat_request,
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

        self.passive_mode = passive_mode

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

        # If 'passive_mode' is set to True, the runtime RSA wrapper
        # become useless since it will not be used anywhere.
        self.rsa_wrapper = (
            (runtime_rsa_wrapper if runtime_rsa_wrapper else RSAWrapper())
            if not passive_mode
            else None
        )

    def __del__(self):
        if self.is_running:
            self._stop_server()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        if self.is_running:
            self._stop_server()

    def _format_traceback(self, exception):
        return "".join(
            traceback.format_exception(
                type(exception), exception, exception.__traceback__
            )
        )

    def _initialize_listen_interface(self):
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_sock.bind((self.bind_address, self.listen_port))
        self.server_sock.listen(5)

    def _terminate_listen_interface(self):
        self.server_sock.close()

    def _execute_event_handler(self, event, context, data={}):
        return_value = None

        if event == EVENT_RUNTIME_ERROR:
            self.recorded_runtime_errors_counter += 1

        if self.event_handler_dict.get(event):
            return_value = self.event_handler_dict[event](context=context, data=data)

            if self.passive_mode:
                return return_value

        if data.get("client_instance") and data.get("client_instance").isClosed():
            return -1

    def _store_container(self, container_instance, forwarder_instance):
        _, _, new_client_token = self.database_interface.addEntry(
            container_instance.getUUID()
        )
        self.virtualization_interface.storeContainer(container_instance)
        self.port_forwarding_interface.storeForwarder(forwarder_instance)

        return new_client_token

    def _delete_container(self, container_instance):
        container_uuid = container_instance.getUUID()

        self.database_interface.deleteEntry(
            self.database_interface.getContainerUUIDEntryID(container_uuid)
        )
        self.virtualization_interface.deleteStoredContainer(container_uuid)
        self.port_forwarding_interface.deleteStoredForwarder(container_uuid)

    # This routine detects inactive container and destroy them in consequence
    def _delete_container_on_domain_shutdown_routine(self):
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
                            container_instance.getUUID()
                        )
                    )

                    if forwarder_instance and forwarder_instance.isForwarding():
                        forwarder_instance.stopForward()

                        self._execute_event_handler(
                            EVENT_FORWARDER_STOPPED,
                            CONTEXT_AUTOMATIC_ACTION,
                            data={"forwarder_instance": forwarder_instance},
                        )

                    self._delete_container(container_instance)

                    # Mark the container instance domain as stopped
                    self._execute_event_handler(
                        EVENT_CONTAINER_DOMAIN_STOPPED,
                        CONTEXT_AUTOMATIC_ACTION,
                        data={"container_instance": container_instance},
                    )

            except Exception as E:
                self._execute_event_handler(
                    EVENT_RUNTIME_ERROR,
                    CONTEXT_ERROR,
                    data={
                        "exception_object": E,
                        "traceback": self._format_traceback(E),
                    },
                )

            time.sleep(1)

    def _delete_all_containers(self):
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

                self._execute_event_handler(
                    EVENT_CONTAINER_DOMAIN_STOPPED,
                    CONTEXT_NORMAL_PROCESS,
                    data={"container_instance": container_instance},
                )

            self._delete_container(container_instance)

    def _start_server(self):
        if not self.passive_mode:
            self._initialize_listen_interface()

        self.start_timestamp = int(time.time())
        self.is_running = True

        threading.Thread(
            target=self._delete_container_on_domain_shutdown_routine
        ).start()

        self._execute_event_handler(EVENT_SERVER_STARTED, CONTEXT_NORMAL_PROCESS)

        if not self.passive_mode:
            self._main_server_loop_routine()

    def _stop_server(self, raise_errors=False, die_on_error=False):
        try:
            self._delete_all_containers()
            self.database_interface.closeDatabase()

            if not self.passive_mode:
                self._terminate_listen_interface()

            self.is_running = False

            self._execute_event_handler(EVENT_SERVER_STOPPED, CONTEXT_NORMAL_PROCESS)

        except Exception as E:
            if raise_errors:
                raise E

            self._execute_event_handler(
                EVENT_RUNTIME_ERROR,
                CONTEXT_ERROR,
                data={
                    "exception_object": E,
                    "traceback": self._format_traceback(E),
                },
            )

            if die_on_error:
                exit(0xDEAD)

    # Intern methods for normal processes
    def _handle_create_request(
        self, client_instance=None, passive_execution=False, **void_kwargs
    ):
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
                self._execute_event_handler(
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
                    self._execute_event_handler(
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
                self._execute_event_handler(
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
                    self._execute_event_handler(
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
                    self._execute_event_handler(
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
                new_container_instance.getIP(),
                new_container_instance.getUUID(),
                22,
                store=False,
            )

            if (
                self._execute_event_handler(
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
                    self._execute_event_handler(
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
            new_client_token = self._store_container(
                new_container_instance, new_forwarder_instance
            )

            data_dict = {
                "container_uuid": new_container_instance.getUUID(),
                "client_token": new_client_token,
                "container_iso_sha256": new_container_instance.makeISOFileChecksum(),
                "container_username": new_container_username,
                "container_password": new_container_password,
                "container_listen_port": new_forwarder_instance.getServerOriginPort(),
            }

            if not passive_execution and client_instance:
                if not client_instance.isClosed():
                    client_instance.sendResponse(
                        True,
                        RESPONSE_MSG_OK,
                        data=data_dict,
                    )

            else:
                return makeResponse(True, RESPONSE_MSG_OK, data=data_dict)[1]

        except Exception as E:
            if (
                self._execute_event_handler(
                    EVENT_RUNTIME_ERROR,
                    CONTEXT_ERROR,
                    data={
                        "exception_object": E,
                        "traceback": self._format_traceback(E),
                        "client_instance": client_instance,
                    },
                )
                == -1
            ):
                return

            if new_forwarder_instance and new_forwarder_instance.isForwarding():
                new_forwarder_instance.stopForward()

                if (
                    self._execute_event_handler(
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

            if (
                new_endpoint_shell_instance
                and not new_endpoint_shell_instance.isClosed()
            ):
                new_endpoint_shell_instance.closeShell()

                if (
                    self._execute_event_handler(
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

            if new_container_instance:
                if new_container_instance.isDomainRunning():
                    new_container_instance.stopDomain()

                    if (
                        self._execute_event_handler(
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

                self._delete_container(new_container_instance)

            # Chech if the error is due to a broken pipe caused by peer,
            # no response will be sent if it is the case
            if not passive_execution and client_instance:
                if (
                    not client_instance.isClosed()
                    and "Peer refused the packet" not in str(E)
                ):
                    client_instance.sendResponse(False, RESPONSE_MSG_INTERNAL_ERROR)

            else:
                return makeResponse(False, RESPONSE_MSG_INTERNAL_ERROR)[1]

    def _handle_destroy_request(
        self,
        client_instance=None,
        passive_execution=False,
        credentials_dict={},
        **void_kwargs,
    ):
        if not passive_execution:
            stored_request = client_instance.getStoredRequest()

            request_container_uuid = stored_request["parameters"].get("container_uuid")
            request_client_token = stored_request["parameters"].get("client_token")

        else:
            request_container_uuid = credentials_dict.get("container_uuid")
            request_client_token = credentials_dict.get("client_token")

        if not self.database_interface.getEntryID(
            request_container_uuid,
            request_client_token,
        ):
            self._execute_event_handler(
                EVENT_AUTHENTICATION_ERROR,
                CONTEXT_ERROR,
                data={"client_instance": client_instance},
            )

            if not passive_execution and client_instance:
                if not client_instance.isClosed():
                    client_instance.sendResponse(False, RESPONSE_MSG_BAD_AUTH)

                return

            else:
                return makeResponse(False, RESPONSE_MSG_BAD_AUTH)[1]

        container_instance = self.virtualization_interface.getStoredContainer(
            request_container_uuid
        )

        if container_instance.isDomainRunning():
            container_instance.stopDomain()

            if (
                self._execute_event_handler(
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
            container_instance.getUUID()
        )

        if forwarder_instance and forwarder_instance.isForwarding():
            forwarder_instance.stopForward()

            if (
                self._execute_event_handler(
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

        self._delete_container(container_instance)

        if not passive_execution and client_instance:
            client_instance.sendResponse(True, RESPONSE_MSG_OK)

        else:
            return makeResponse(True, RESPONSE_MSG_OK)[1]

    def _handle_stat_request(
        self, client_instance=None, passive_execution=False, **void_kwargs
    ):
        _, _, uptime = self.getRuntimeStatistics()

        runtime_statistics_dict = {
            "version": __version__,
            "uptime": uptime,
        }

        if not passive_execution and client_instance:
            client_instance.sendResponse(
                True,
                RESPONSE_MSG_OK,
                data=runtime_statistics_dict,
            )

        else:
            return makeResponse(True, RESPONSE_MSG_OK, data=runtime_statistics_dict)[1]

    def _handle_new_client(self, client_instance):
        try:
            (
                is_recv_request_conform,
                recv_request_content,
                _,
            ) = client_instance.recvRequest()

            if not is_recv_request_conform:
                self._execute_event_handler(
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

                    self._execute_event_handler(
                        EVENT_CLIENT_CLOSED,
                        CONTEXT_HANDLE_END,
                        data={"client_instance": client_instance},
                    )

                return

            if not self.request_handler_dict.get(recv_request_content["verb"]):
                self._execute_event_handler(
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

                    self._execute_event_handler(
                        EVENT_CLIENT_CLOSED,
                        CONTEXT_HANDLE_END,
                        data={"client_instance": client_instance},
                    )

                return

            if (
                self._execute_event_handler(
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

                self._execute_event_handler(
                    EVENT_CLIENT_CLOSED,
                    CONTEXT_HANDLE_END,
                    data={"client_instance": client_instance},
                )

        except Exception as E:
            self._execute_event_handler(
                EVENT_RUNTIME_ERROR,
                CONTEXT_ERROR,
                data={
                    "exception_object": E,
                    "traceback": self._format_traceback(E),
                    "client_instance": client_instance,
                },
            )

            if not client_instance.isClosed():
                client_instance.sendResponse(
                    False,
                    RESPONSE_MSG_INTERNAL_ERROR,
                )

                client_instance.closeConnection()

                self._execute_event_handler(
                    EVENT_CLIENT_CLOSED,
                    CONTEXT_HANDLE_END,
                    data={"client_instance": client_instance},
                )

    def _main_server_loop_routine(self):
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
                    self._execute_event_handler(
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
                    self._execute_event_handler(
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
                    target=self._handle_new_client, args=[new_client_instance]
                ).start()

            except Exception as E:
                data = {
                    "exception_object": E,
                    "traceback": self._format_traceback(E),
                    "client_socket": new_client_socket,
                }

                if new_client_instance:
                    data.update({"client_instance": new_client_instance})

                self._execute_event_handler(
                    EVENT_RUNTIME_ERROR, CONTEXT_ERROR, data=data
                )

                if new_client_instance and not new_client_instance.isClosed():
                    new_client_instance.sendResponse(False, RESPONSE_MSG_INTERNAL_ERROR)

                    new_client_instance.closeConnection()

                    self._execute_event_handler(
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
    def isRunning(self) -> bool:
        return self.is_running

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
            (int(time.time()) - self.start_timestamp) if self.is_running else 0,
        )

    def getRequestHandler(self, verb: str) -> Union[None, Callable]:
        return self.request_handler_dict.get(verb)

    def getEventHandler(self, event: str) -> Union[None, Callable]:
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

    def setEventHandler(self, event: str, routine: Callable) -> None:
        self.event_handler_dict.update({event: routine})

    def executeRequestHandler(
        self,
        verb: str,
        client_instance: ClientInstance = None,
        data: dict = {},
    ) -> dict:
        if not self.request_handler_dict.get(verb):
            raise RuntimeError(f"The verb '{verb}' is not handled")

        return self.request_handler_dict[verb](
            client_instance=client_instance,
            passive_execution=not client_instance or self.passive_mode,
            credentials_dict=data,
        )

    def triggerEvent(
        self, event: str, context: int = CONTEXT_DEFERRED_CALL, data: dict = {}
    ) -> Any:
        if event not in self.event_handler_dict.keys():
            raise RuntimeError(f"The event '{event}' does not exists")

        return self._execute_event_handler(event=event, context=context, data=data)

    def startServer(self) -> None:
        if self.is_running:
            raise RuntimeError("Server is already running")

        self._start_server()

    def stopServer(self, die_on_error: bool = DEFAULT_DIE_ON_ERROR) -> None:
        if not self.is_running:
            if die_on_error:
                return

            raise RuntimeError("Server is already stopped")

        self._stop_server(raise_errors=True, die_on_error=die_on_error)
