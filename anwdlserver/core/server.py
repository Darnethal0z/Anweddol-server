"""
	Copyright 2023 The Anweddol project
	See the LICENSE file for licensing informations
	---

	Server features

"""
import multiprocessing
import threading
import traceback
import socket
import time


# Intern importation
from .virtualization import VirtualizationInterface
from .database import DatabaseInterface
from .client import ClientInstance
from .util import isSocketClosed
from .crypto import RSAWrapper


# Default parameters
DEFAULT_SERVER_BIND_ADDRESS = ""
DEFAULT_SERVER_LISTEN_PORT = 6150
DEFAULT_CLIENT_TIMEOUT = 10

DEFAULT_ASYCHRONOUS = False


# Constants definition
REQUEST_VERB_CREATE = "CREATE"
REQUEST_VERB_DESTROY = "DESTROY"
REQUEST_VERB_STAT = "STAT"

RESPONSE_MSG_OK = "OK"
RESPONSE_MSG_BAD_AUTH = "Bad authentication"
RESPONSE_MSG_BAD_REQ = "Bad request"
RESPONSE_MSG_REFUSED_REQ = "Refused request"
RESPONSE_MSG_UNAVAILABLE = "Unavailable"
RESPONSE_MSG_INTERNAL_ERROR = "Internal error"

EVENT_CLIENT = 1
EVENT_CLIENT_CLOSED = 2
EVENT_CONNECTION = 3
EVENT_CREATED_CONTAINER = 4
EVENT_CREATED_ENDPOINT_SHELL = 5
EVENT_DESTROYED_CONTAINER = 6
EVENT_MALFORMED_REQUEST = 7
EVENT_REQUEST = 8
EVENT_RUNTIME_ERROR = 9
EVENT_STARTED = 10
EVENT_STOPPED = 11
EVENT_UNKNOWN_VERB = 12


class ServerInterface:
    def __init__(
        self,
        container_iso_path: str = None,
        bind_address: str = DEFAULT_SERVER_BIND_ADDRESS,
        listen_port: int = DEFAULT_SERVER_LISTEN_PORT,
        client_timeout: int = DEFAULT_CLIENT_TIMEOUT,
        runtime_virtualization_interface: VirtualizationInterface = None,
        runtime_database_interface: DatabaseInterface = None,
        runtime_rsa_wrapper: RSAWrapper = None,
    ):
        # Intern variables
        self.request_handler_dict = {
            REQUEST_VERB_CREATE: self.__handle_create_request,
            REQUEST_VERB_DESTROY: self.__handle_destroy_request,
            REQUEST_VERB_STAT: self.__handle_stat_request,
        }

        self.event_handler_dict = {
            EVENT_CLIENT: None,
            EVENT_CLIENT_CLOSED: None,
            EVENT_CONNECTION: None,
            EVENT_CREATED_CONTAINER: None,
            EVENT_CREATED_ENDPOINT_SHELL: None,
            EVENT_DESTROYED_CONTAINER: None,
            EVENT_MALFORMED_REQUEST: None,
            EVENT_REQUEST: None,
            EVENT_RUNTIME_ERROR: None,
            EVENT_STARTED: None,
            EVENT_STOPPED: None,
            EVENT_UNKNOWN_VERB: None,
        }

        self.bind_address = bind_address
        self.listen_port = listen_port
        self.client_timeout = client_timeout

        self.recorded_runtime_errors_counter = 0
        self.main_process_handler = None
        self.start_timestamp = None
        self.server_sock = None
        self.is_running = False

        self.virtualization_interface = (
            runtime_virtualization_interface
            if runtime_virtualization_interface
            else VirtualizationInterface(container_iso_path)
        )
        self.database_interface = (
            runtime_database_interface
            if runtime_database_interface
            else DatabaseInterface()
        )
        self.runtime_rsa_wrapper = (
            runtime_rsa_wrapper if runtime_rsa_wrapper else RSAWrapper()
        )

    def __del__(self):
        if self.is_running:
            self.stopServer()

    # Intern methods for normal processes
    def __handle_create_request(self, client_instance):
        if self.virtualization_interface.getAvailableContainersAmount() <= 0:
            client_instance.sendResponse(
                False,
                RESPONSE_MSG_UNAVAILABLE,
                reason="Running containers maximum amount was reached",
            )
            client_instance.closeConnection()
            if self.event_handler_dict.get(EVENT_CLIENT_CLOSED):
                self.event_handler_dict[EVENT_CLIENT_CLOSED](
                    client_instance=client_instance
                )
            return

        # We do not store immediatly the container since errors
        # can occur during setup, leaving the container instance in an
        # unstable state.
        new_container_instance = self.virtualization_interface.createContainer(
            store=False
        )

        if self.event_handler_dict.get(EVENT_CREATED_CONTAINER):
            self.event_handler_dict[EVENT_CREATED_CONTAINER](
                client_instance=client_instance,
                container_instance=new_container_instance,
            )

            if client_instance.isClosed():
                return

        if not new_container_instance.isDomainRunning():
            new_container_instance.startDomain()

        new_container_shell = new_container_instance.createEndpointShell()

        if self.event_handler_dict.get(EVENT_CREATED_ENDPOINT_SHELL):
            self.event_handler_dict[EVENT_CREATED_ENDPOINT_SHELL](
                endpoint_shell_instance=new_container_shell,
                container_instance=new_container_instance,
                client_instance=client_instance,
            )

            if client_instance.isClosed():
                new_container_shell.closeShell()
                return

        if not new_container_shell.isClosed():
            container_ssh_credentials_tuple = (
                new_container_shell.generateContainerSSHCredentials()
            )

            # close_on_done is set to True, the shell will be automatically closed within the method
            new_container_shell.setContainerSSHCredentials(
                username=container_ssh_credentials_tuple[0],
                password=container_ssh_credentials_tuple[1],
                listen_port=container_ssh_credentials_tuple[2],
            )

            new_container_shell.closeShell()

        else:
            container_ssh_credentials_tuple = (
                new_container_shell.getStoredContainerSSHCredentials()
            )

        # Once everything is done without errors, we can store it.
        created_entry = self.database_interface.addEntry(
            new_container_instance.getUUID()
        )
        self.virtualization_interface.addStoredContainer(new_container_instance)

        try:
            client_instance.sendResponse(
                True,
                RESPONSE_MSG_OK,
                data={
                    "container_uuid": new_container_instance.getUUID(),
                    "client_token": created_entry[2],
                    "container_iso_sha256": new_container_instance.makeISOChecksum(),
                    "container_username": container_ssh_credentials_tuple[0],
                    "container_password": container_ssh_credentials_tuple[1],
                    "container_listen_port": container_ssh_credentials_tuple[2],
                },
            )

        except Exception as E:
            # If we can't transmit those informations to the client, we must
            # delete them since the container becomes unusable, and the session credentials useless.
            new_container_instance.stopDomain()

            self.database_interface.deleteEntry(created_entry[0])
            self.virtualization_interface.deleteStoredContainer(
                new_container_instance.getUUID()
            )

            self.recorded_runtime_errors_counter += 1

            if self.event_handler_dict.get(EVENT_RUNTIME_ERROR):
                self.event_handler_dict[EVENT_RUNTIME_ERROR](
                    name="__handle_create_request",
                    client_instance=client_instance,
                    ex_class=E,
                    traceback="".join(
                        traceback.format_exception(None, E, E.__traceback__)
                    ),
                )

    def __handle_destroy_request(self, client_instance):
        request_container_uuid = client_instance.getStoredRequest()["parameters"].get(
            "container_uuid"
        )

        credentials_entry_tuple = self.database_interface.getEntryID(
            request_container_uuid,
            client_instance.getStoredRequest()["parameters"].get("client_token"),
        )

        if not credentials_entry_tuple:
            client_instance.sendResponse(False, RESPONSE_MSG_BAD_AUTH)
            return

        container_instance = self.virtualization_interface.getStoredContainer(
            request_container_uuid
        )
        container_instance.stopDomain()

        self.database_interface.deleteEntry(credentials_entry_tuple[0])
        self.virtualization_interface.deleteStoredContainer(request_container_uuid)

        if self.event_handler_dict.get(EVENT_DESTROYED_CONTAINER):
            self.event_handler_dict[EVENT_DESTROYED_CONTAINER](
                client_instance=client_instance,
                container_instance=container_instance,
            )

            if client_instance.isClosed():
                return

        client_instance.sendResponse(True, RESPONSE_MSG_OK)

    def __handle_stat_request(self, client_instance):
        client_instance.sendResponse(
            True,
            RESPONSE_MSG_OK,
            data={
                "uptime": int(time.time()) - self.start_timestamp,
                "available": self.virtualization_interface.getAvailableContainersAmount(),
            },
        )

    def __handle_new_client(self, client_instance):
        try:
            if self.event_handler_dict.get(EVENT_CLIENT):
                self.event_handler_dict[EVENT_CLIENT](client_instance=client_instance)

                if client_instance.isClosed():
                    return

            if not client_instance.getStoredRequest():
                recv_request = client_instance.recvRequest()
                if not recv_request[0]:
                    # Since the request is malformed, exit the procedure

                    if self.event_handler_dict.get(EVENT_MALFORMED_REQUEST):
                        self.event_handler_dict[EVENT_MALFORMED_REQUEST](
                            client_instance=client_instance,
                            cerberus_error_dict=recv_request[1],
                        )

                        if not client_instance.isClosed():
                            client_instance.sendResponse(
                                False,
                                RESPONSE_MSG_BAD_REQ,
                                reason=f"Malformed request : {recv_request[1]}",
                            )

                            client_instance.closeConnection()

                            if self.event_handler_dict.get(EVENT_CLIENT_CLOSED):
                                self.event_handler_dict[EVENT_CLIENT_CLOSED](
                                    client_instance=client_instance
                                )

                        return

                if self.event_handler_dict.get(EVENT_REQUEST):
                    self.event_handler_dict[EVENT_REQUEST](
                        client_instance=client_instance
                    )

                    if client_instance.isClosed():
                        return

            if not self.request_handler_dict.get(recv_request[1]["verb"]):
                # Since the verb is unknown, exit the procedure

                if self.event_handler_dict.get(EVENT_UNKNOWN_VERB):
                    self.event_handler_dict[EVENT_UNKNOWN_VERB](
                        client_instance=client_instance
                    )

                    if not client_instance.isClosed():
                        client_instance.sendResponse(
                            False,
                            RESPONSE_MSG_BAD_REQ,
                            reason="Unknown verb",
                        )
                        client_instance.closeConnection()

                        if self.event_handler_dict.get(EVENT_CLIENT_CLOSED):
                            self.event_handler_dict[EVENT_CLIENT_CLOSED](
                                client_instance=client_instance
                            )

                    return

            self.request_handler_dict[recv_request[1]["verb"]](
                client_instance=client_instance
            )

            if not client_instance.isClosed():
                client_instance.closeConnection()

                if self.event_handler_dict.get(EVENT_CLIENT_CLOSED):
                    self.event_handler_dict[EVENT_CLIENT_CLOSED](
                        client_instance=client_instance
                    )

        except Exception as E:
            self.recorded_runtime_errors_counter += 1

            if self.event_handler_dict.get(EVENT_RUNTIME_ERROR):
                self.event_handler_dict[EVENT_RUNTIME_ERROR](
                    name="__handle_new_client",
                    client_instance=client_instance,
                    ex_class=E,
                    traceback="".join(
                        traceback.format_exception(None, E, E.__traceback__)
                    ),
                )

            if not client_instance.isClosed():
                client_instance.sendResponse(
                    False,
                    RESPONSE_MSG_INTERNAL_ERROR,
                )

                client_instance.closeConnection()

                if self.event_handler_dict.get(EVENT_CLIENT_CLOSED):
                    self.event_handler_dict[EVENT_CLIENT_CLOSED](
                        client_instance=client_instance
                    )

    def __main_server_loop_routine(self):
        while self.is_running:
            try:
                new_client_socket = self.server_sock.accept()[0]

            except OSError:
                break

            try:
                new_client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

                if self.client_timeout:
                    new_client_socket.settimeout(self.client_timeout)

                if self.event_handler_dict.get(EVENT_CONNECTION):
                    self.event_handler_dict[EVENT_CONNECTION](
                        client_socket=new_client_socket
                    )

                    if isSocketClosed(new_client_socket):
                        pass

                new_client_instance = ClientInstance(
                    new_client_socket,
                    timeout=self.client_timeout,
                    rsa_wrapper=self.runtime_rsa_wrapper,
                )

                threading.Thread(
                    target=self.__handle_new_client, args=[new_client_instance]
                ).start()

            except Exception as E:
                new_client_socket.close()

                self.recorded_runtime_errors_counter += 1

                if self.event_handler_dict.get(EVENT_RUNTIME_ERROR):
                    self.event_handler_dict[EVENT_RUNTIME_ERROR](
                        name="__main_server_loop_routine",
                        ex_class=E,
                        traceback="".join(
                            traceback.format_exception(None, E, E.__traceback__)
                        ),
                    )

    # Detects stopped container domains and update the database in consequence
    def __update_database_on_domain_shutdown_routine(self):
        while self.is_running:
            try:
                for container in self.virtualization_interface.listStoredContainers():
                    if not container.isDomainRunning():
                        container_entry_id = self.database_interface.getValueEntryID(
                            container.getUUID()
                        )

                        self.database_interface.deleteEntry(container_entry_id)
                        self.virtualization_interface.deleteStoredContainer(
                            container.getUUID()
                        )

                time.sleep(1)

            except Exception as E:
                self.recorded_runtime_errors_counter += 1

                if self.event_handler_dict.get(EVENT_RUNTIME_ERROR):
                    self.event_handler_dict[EVENT_RUNTIME_ERROR](
                        name="__update_database_on_domain_shutdown_routine",
                        ex_class=E,
                        traceback="".join(
                            traceback.format_exception(None, E, E.__traceback__)
                        ),
                    )

    # Event decorators binding for external scripts callback
    @property
    def on_client(self):
        def wrapper(routine):
            self.event_handler_dict.update({EVENT_CLIENT: routine})
            return wrapper

        return wrapper

    @property
    def on_client_closed(self):
        def wrapper(routine):
            self.event_handler_dict.update({EVENT_CLIENT_CLOSED: routine})
            return wrapper

        return wrapper

    @property
    def on_connection(self):
        def wrapper(routine):
            self.event_handler_dict.update({EVENT_CONNECTION: routine})
            return wrapper

        return wrapper

    @property
    def on_created_container(self):
        def wrapper(routine):
            self.event_handler_dict.update({EVENT_CREATED_CONTAINER: routine})
            return wrapper

        return wrapper

    @property
    def on_created_endpoint_shell(self):
        def wrapper(routine):
            self.event_handler_dict.update({EVENT_CREATED_ENDPOINT_SHELL: routine})
            return wrapper

        return wrapper

    @property
    def on_destroyed_container(self):
        def wrapper(routine):
            self.event_handler_dict.update({EVENT_DESTROYED_CONTAINER: routine})
            return wrapper

        return wrapper

    @property
    def on_malformed_request(self):
        def wrapper(routine):
            self.event_handler_dict.update({EVENT_MALFORMED_REQUEST: routine})
            return wrapper

        return wrapper

    @property
    def on_request(self):
        def wrapper(routine):
            self.event_handler_dict.update({EVENT_REQUEST: routine})
            return wrapper

        return wrapper

    @property
    def on_runtime_error(self):
        def wrapper(routine):
            self.event_handler_dict.update({EVENT_RUNTIME_ERROR: routine})
            return wrapper

        return wrapper

    @property
    def on_started(self):
        def wrapper(routine):
            self.event_handler_dict.update({EVENT_STARTED: routine})
            return wrapper

        return wrapper

    @property
    def on_stopped(self):
        def wrapper(routine):
            self.event_handler_dict.update({EVENT_STOPPED: routine})
            return wrapper

        return wrapper

    @property
    def on_unknown_verb(self):
        def wrapper(routine):
            self.event_handler_dict.update({EVENT_UNKNOWN_VERB: routine})
            return wrapper

        return wrapper

    # Utility methods
    def getRuntimeDatabaseInterface(self) -> DatabaseInterface:
        return self.database_interface

    def getRuntimeVirtualizationInterface(self) -> VirtualizationInterface:
        return self.runtime_virtualization_interface

    def getRuntimeRSAWrapper(self) -> RSAWrapper:
        return self.runtime_rsa_wrapper

    def getRuntimeStatistics(self) -> tuple:
        return (
            self.is_running,
            self.recorded_runtime_errors_counter,
            int(time.time()) - self.start_timestamp,
            self.virtualization_interface.getAvailableContainersAmount(),
        )

    def setRequestHandler(self, verb: str, routine: callable) -> None:
        self.request_handler_dict.update({verb: routine})

    def setEventHandler(self, event: int, routine: callable) -> None:
        self.event_handler_dict.update({event: routine})

    def startServer(self, asynchronous: bool = DEFAULT_ASYCHRONOUS) -> None:
        try:
            self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_sock.bind((self.bind_address, self.listen_port))
            self.server_sock.listen(5)

            # (*)
            threading.Thread(
                target=self.__update_database_on_domain_shutdown_routine
            ).start()

            self.is_running = True
            self.start_timestamp = int(time.time())

            if self.event_handler_dict.get(EVENT_STARTED):
                self.event_handler_dict[EVENT_STARTED]()

            if asynchronous:
                self.main_process_handler = multiprocessing.Process(
                    target=self.__main_server_loop_routine
                ).start()

        except Exception as E:
            self.recorded_runtime_errors_counter += 1

            if self.event_handler_dict.get(EVENT_RUNTIME_ERROR):
                self.event_handler_dict[EVENT_RUNTIME_ERROR](
                    name="startServer",
                    ex_class=E,
                    traceback="".join(
                        traceback.format_exception(None, E, E.__traceback__)
                    ),
                )

            return

        self.__main_server_loop_routine()

    def stopServer(self) -> None:
        try:
            if self.main_process_handler:
                self.main_process_handler.terminate()

            self.is_running = False

            self.server_sock.shutdown(2)
            self.server_sock.close()

            for container_uuid in self.virtualization_interface.listStoredContainers():
                self.virtualization_interface.getStoredContainer(
                    container_uuid
                ).stopDomain()
                # Do not delete the stored container, else will raise
                # a RuntimeError("dictionary changed size during iteration")

            self.database_interface.closeDatabase()

            if self.event_handler_dict.get(EVENT_STOPPED):
                self.event_handler_dict[EVENT_STOPPED]()

        except Exception as E:
            self.recorded_runtime_errors_counter += 1

            if self.event_handler_dict.get(EVENT_RUNTIME_ERROR):
                self.event_handler_dict[EVENT_RUNTIME_ERROR](
                    name="stopServer",
                    ex_class=E,
                    traceback="".join(
                        traceback.format_exception(None, E, E.__traceback__)
                    ),
                )

    def restartServer(self, asynchronous: bool = DEFAULT_ASYCHRONOUS) -> None:
        try:
            self.stopServer()
            self.startServer(asynchronous=asynchronous)

        except Exception as E:
            self.recorded_runtime_errors_counter += 1

            if self.event_handler_dict.get(EVENT_RUNTIME_ERROR):
                self.event_handler_dict[EVENT_RUNTIME_ERROR](
                    name="restartServer",
                    ex_class=E,
                    traceback="".join(
                        traceback.format_exception(None, E, E.__traceback__)
                    ),
                )
