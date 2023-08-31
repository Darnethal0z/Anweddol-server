"""
    Copyright 2023 The Anweddol project
    See the LICENSE file for licensing informations
    ---

    CLI : Main server process functions

"""
from zipfile import ZipFile
import threading
import datetime
import logging
import getpass
import signal
import time
import os

# Intern importation
from .core.server import (
    ServerInterface,
    RESPONSE_MSG_BAD_REQ,
    RESPONSE_MSG_BAD_AUTH,
    RESPONSE_MSG_OK,
    RESPONSE_MSG_UNAVAILABLE,
    RESPONSE_MSG_INTERNAL_ERROR,
    REQUEST_VERB_STAT,
    REQUEST_VERB_CREATE,
)
from .core.crypto import RSAWrapper

from .tools.access_token import AccessTokenManager
from .utilities import createFileRecursively


# Constants definition
LOG_INFO = "INFO: "
LOG_WARN = "WARNING: "
LOG_ERROR = "ERROR: "

# Default parameters
DEFAULT_ENABLE_STDOUT_LOG = False
DEFAULT_ENABLE_TRACEBACK_ON_LOG = False


class AnweddolServerProcess:
    def __init__(
        self,
        config_content,
        enable_stdout_log=DEFAULT_ENABLE_STDOUT_LOG,
        enable_traceback_on_log=DEFAULT_ENABLE_TRACEBACK_ON_LOG,
    ):
        self.enable_stdout_log = enable_stdout_log
        self.enable_traceback_on_log = enable_traceback_on_log

        self.config_content = config_content
        self.access_token_manager = None
        self.runtime_rsa_wrapper = None
        self.server_interface = None
        self.is_running = False

        self.actual_running_container_domains_counter = 0

        try:
            logging.basicConfig(
                format="%(asctime)s %(levelname)s : %(message)s",
                filename=self.config_content["server"].get("log_file_path"),
                level=logging.INFO,
                encoding="utf-8",
                filemode="a",
            )

        except Exception as E:
            raise RuntimeError(f"FATAL : Cannot load log file ({E})")

    def __log(self, kind, message):
        if kind == LOG_INFO:
            logging.info(message)
        elif kind == LOG_WARN:
            logging.warning(message)
        else:
            logging.error(message)

        if self.enable_stdout_log:
            print(str(datetime.datetime.now()) + " " + kind + message)

    def __log_rotate_routine(self):
        while self.is_running:
            with open(self.config_content["server"].get("log_file_path"), "r") as fd:
                if sum(1 for line in fd.readlines()) >= self.config_content[
                    "log_rotation"
                ].get("max_log_lines_amount"):
                    if not os.path.exists(
                        self.config_content["log_rotation"].get(
                            "log_archive_folder_path"
                        )
                    ):
                        os.mkdir(
                            self.config_content["log_rotation"].get(
                                "log_archive_folder_path"
                            )
                        )

                    if self.config_content["log_rotation"].get("action") == "archive":
                        new_archive_name = f"archived_{datetime.datetime.now()}.zip"
                        ZipFile(
                            self.config_content["log_rotation"].get(
                                "log_archive_folder_path"
                            )
                            + (
                                "/"
                                if self.config_content["log_rotation"].get(
                                    "log_archive_folder_path"
                                )[-1]
                                != "/"
                                else ""
                            )
                            + new_archive_name,
                            "w",
                        ).write(self.config_content["server"].get("log_file_path"))

                    with open(
                        self.config_content["server"].get("log_file_path"), "w"
                    ) as fd:
                        fd.close()

            time.sleep(1)

    def __handle_stat_request(self, **kwargs):
        client_instance = kwargs.get("client_instance")
        client_id = kwargs.get("client_instance").getID()

        try:
            runtime_statistics = self.server_interface.getRuntimeStatistics()
            max_allowed_running_container_domains = self.config_content[
                "container"
            ].get("max_allowed_running_container_domains")

            client_instance.sendResponse(
                True,
                RESPONSE_MSG_OK,
                data={
                    "uptime": runtime_statistics[2],
                    "available": (
                        max_allowed_running_container_domains
                        - self.actual_running_container_domains_counter
                    )
                    if max_allowed_running_container_domains
                    else "nolimit",
                },
            )

            client_instance.closeConnection()

            self.__log(LOG_INFO, f"(client ID {client_id}) Connection closed")

        except Exception as E:
            client_instance.sendResponse(False, RESPONSE_MSG_INTERNAL_ERROR)

            client_instance.closeConnection()

            self.__log(LOG_INFO, f"(client ID {client_id}) Connection closed")

            raise E

    def initializeProcess(self):
        try:
            self.__log(
                LOG_WARN,
                f"Initializing server (running as '{getpass.getuser()}') ...",
            )

            self.__log(LOG_INFO, "Loading instance RSA key pair ...")

            public_key_path = self.config_content["server"].get(
                "public_rsa_key_file_path"
            )
            private_key_path = self.config_content["server"].get(
                "private_rsa_key_file_path"
            )

            if not self.config_content["server"].get("enable_onetime_rsa_keys"):
                if not os.path.exists(private_key_path):
                    createFileRecursively(private_key_path)

                    self.runtime_rsa_wrapper = RSAWrapper()

                    with open(public_key_path, "w") as fd:
                        fd.write(self.runtime_rsa_wrapper.getPublicKey().decode())

                    with open(private_key_path, "w") as fd:
                        fd.write(self.runtime_rsa_wrapper.getPrivateKey().decode())

                else:
                    self.runtime_rsa_wrapper = RSAWrapper(generate_key_pair=False)

                    with open(private_key_path, "r") as fd:
                        self.runtime_rsa_wrapper.setPrivateKey(
                            fd.read().encode(),
                            derivate_public_key=not os.path.exists(public_key_path),
                        )

                    if not os.path.exists(public_key_path):
                        with open(public_key_path, "w") as fd:
                            fd.write(self.runtime_rsa_wrapper.getPublicKey().decode())

                    else:
                        with open(public_key_path, "r") as fd:
                            self.runtime_rsa_wrapper.setPublicKey(fd.read().encode())

            self.__log(LOG_INFO, "Initializing server interface ...")

            self.server_interface = ServerInterface(
                runtime_container_iso_file_path=self.config_content["container"].get(
                    "container_iso_file_path"
                ),
                bind_address=self.config_content["server"].get("bind_address"),
                listen_port=self.config_content["server"].get("listen_port"),
                client_timeout=self.config_content["server"].get("timeout"),
                runtime_rsa_wrapper=self.runtime_rsa_wrapper,
            )

            if self.config_content["access_token"].get("enabled"):
                self.__log(LOG_INFO, "Loading access token database ...")
                self.access_token_manager = AccessTokenManager(
                    self.config_content["container"].get(
                        "access_tokens_database_file_path"
                    )
                )

            self.__log(LOG_INFO, "Binding handlers routine ...")

            self.server_interface.setRequestHandler(
                REQUEST_VERB_STAT, self.__handle_stat_request
            )

            @self.server_interface.on_container_created
            def handle_container_creation(context, data):
                container_instance = data.get("container_instance")
                client_id = data.get("client_instance").getID()

                max_allowed_running_container_domains = self.config_content[
                    "container"
                ].get("max_allowed_running_container_domains")

                self.__log(
                    LOG_INFO,
                    f"(client ID {client_id}) Container {container_instance.getUUID()} was created",
                )
                self.__log(
                    LOG_INFO,
                    f"(client ID {client_id}) Actual running containers amount : {self.actual_running_container_domains_counter}/{max_allowed_running_container_domains}",
                )

                container_instance.setMemory(
                    self.config_content["container"].get("container_memory")
                )
                container_instance.setVCPUs(
                    self.config_content["container"].get("container_vcpus")
                )
                container_instance.setNATInterfaceName(
                    self.config_content["container"].get("nat_interface_name")
                )
                container_instance.setISOFilePath(
                    self.config_content["container"].get("container_iso_path")
                )

            @self.server_interface.on_connection_accepted
            def handle_new_connection(context, data):
                if self.config_content["ip_filter"].get("enabled"):
                    client_socket = data.get("client_socket")

                    if "any" in self.config_content["ip_filter"].get("denied_ip_list"):
                        if client_socket.getpeername()[0] not in self.config_content[
                            "ip_filter"
                        ].get("allowed_ip_list") and "any" not in self.config_content[
                            "ip_filter"
                        ].get(
                            "allowed_ip_list"
                        ):
                            client_socket.shutdown(2)
                            client_socket.close()

                            self.__log(
                                LOG_WARN,
                                f"(unspec) Denied ip : {client_socket.getpeername()[0]} (IP not allowed)",
                            )

                            return

                    if client_socket.getpeername()[0] in self.config_content[
                        "ip_filter"
                    ].get("denied_ip_list"):
                        client_socket.shutdown(2)
                        client_socket.close()

                        self.__log(
                            LOG_WARN,
                            f"(unspec) Denied ip : {client_socket.getpeername()[0]} (Denied IP)",
                        )

                        return

                    self.__log(LOG_INFO, "(unspec) IP allowed")

            @self.server_interface.on_client_initialized
            def handle_new_client(context, data):
                client_id = data.get("client_instance").getID()

                self.__log(LOG_INFO, f"(client ID {client_id}) New client connected")

            @self.server_interface.on_request
            def handle_request(context, data):
                client_instance = data.get("client_instance")
                client_id = data.get("client_instance").getID()

                client_request = client_instance.getStoredRequest()
                request_verb = client_instance.getStoredRequest().get("verb")

                self.__log(
                    LOG_INFO, f"(client ID {client_id}) Received {request_verb} request"
                )

                if self.config_content.get("access_token").get("enabled"):
                    if not client_request["parameters"].get("access_token"):
                        client_instance.sendResponse(
                            False,
                            RESPONSE_MSG_BAD_REQ,
                            reason="Access token is required",
                        )
                        self.__log(
                            LOG_WARN,
                            f"(client ID {client_id}) Access authentication failed (No access token provided)",
                        )

                        client_instance.closeConnection()

                        self.__log(
                            LOG_INFO, f"(client ID {client_id}) Connection closed"
                        )

                        return

                    if not self.access_token_manager.getEntryID(
                        client_request["parameters"].get("access_token")
                    ):
                        client_instance.sendResponse(
                            False, RESPONSE_MSG_BAD_AUTH, reason="Invalid access token"
                        )
                        self.__log(
                            LOG_WARN,
                            f"(client ID {client_id}) Access authentication failed (Invalid access token)",
                        )

                        client_instance.closeConnection()

                        self.__log(
                            LOG_INFO, f"(client ID {client_id}) Connection closed"
                        )

                        return

                    self.__log(
                        LOG_INFO,
                        f"(client ID {client_id}) Access authentication success",
                    )

                if (
                    request_verb == REQUEST_VERB_CREATE
                    and self.actual_running_container_domains_counter
                    >= self.config_content["container"].get(
                        "max_allowed_running_container_domains"
                    )
                ):
                    client_instance.sendResponse(
                        False,
                        RESPONSE_MSG_UNAVAILABLE,
                        reason="The maximum allowed amount of running containers has been reached on the server",
                    )
                    self.__log(
                        LOG_WARN,
                        f"(client ID {client_id}) Maximum allowed amount of running containers has been reached",
                    )

                    client_instance.closeConnection()
                    self.__log(LOG_INFO, f"(client ID {client_id}) Connection closed")

            @self.server_interface.on_server_stopped
            def handle_stopped(context, data):
                self.__log(LOG_INFO, "Server is stopped")

                if self.config_content["access_token"].get("enabled"):
                    self.access_token_manager.closeDatabase()

            @self.server_interface.on_server_started
            def notify_started(context, data):
                self.__log(LOG_INFO, "Server is started")

            @self.server_interface.on_endpoint_shell_created
            def handle_endpoint_shell_creation(context, data):
                client_id = data.get("client_instance").getID()
                endpoint_shell_instance = data.get("endpoint_shell_instance")

                endpoint_shell_instance.setEndpointCredentials(
                    self.config_content["container"].get("endpoint_username"),
                    self.config_content["container"].get("endpoint_password"),
                    self.config_content["container"].get("endpoint_listen_port"),
                )

                self.__log(LOG_INFO, f"(client ID {client_id}) Endpoint shell created")

            @self.server_interface.on_client_closed
            def notify_client_closed(context, data):
                client_id = data.get("client_instance").getID()

                self.__log(LOG_INFO, f"(client ID {client_id}) Connection closed")

            @self.server_interface.on_malformed_request
            def notify_malformed_request(context, data):
                client_id = data.get("client_instance").getID()

                self.__log(
                    LOG_WARN, f"(client ID {client_id}) Received malformed request"
                )

            @self.server_interface.on_unhandled_verb
            def notify_unhandled_verb(context, data):
                verb = data.get("client_instance").getStoredRequest()["verb"]
                client_id = data.get("client_instance").getID()

                self.__log(
                    LOG_WARN,
                    f"(client ID {client_id}) Received unhandled verb : '{verb}'",
                )

            @self.server_interface.on_container_domain_started
            def notify_container_domain_started(context, data):
                container_uuid = data.get("container_instance").getUUID()
                container_ip = data.get("container_instance").getIP()
                client_id = data.get("client_instance").getID()

                self.actual_running_container_domains_counter += 1

                self.__log(
                    LOG_INFO,
                    f"(client ID {client_id}) Container {container_uuid} domain is running",
                )
                self.__log(
                    LOG_INFO,
                    f"(client ID {client_id}) Container IP : {container_ip}",
                )

            @self.server_interface.on_container_domain_stopped
            def notify_stopped_container_domain(context, data):
                container_uuid = data.get("container_instance").getUUID()
                client_id = (
                    data.get("client_instance").getID()
                    if data.get("client_instance")
                    else "unspec"
                )

                self.actual_running_container_domains_counter -= 1

                self.__log(
                    LOG_INFO,
                    f"(client ID {client_id}) Container {container_uuid} domain was stopped",
                )

            @self.server_interface.on_endpoint_shell_closed
            def notify_closed_endpoint_shell(context, data):
                client_id = data.get("client_instance").getID()

                self.__log(
                    LOG_INFO, f"(client ID {client_id}) Endpoint shell was closed"
                )

            @self.server_interface.on_runtime_error
            def notify_runtime_error(context, data):
                client_id = (
                    data.get("client_instance").getID()
                    if data.get("client_instance")
                    else "unspec"
                )
                exception_type = type(data.get("ex_class"))
                exception_class = data.get("ex_class")

                self.__log(
                    LOG_ERROR,
                    f"(client ID {client_id}) {exception_type} : {exception_class}",
                )

                if self.enable_traceback_on_log:
                    traceback = data.get("traceback")
                    self.__log(LOG_ERROR, f" -> {traceback}")

            @self.server_interface.on_authentication_error
            def notify_authentication_error(context, data):
                client_id = data.get("client_instance").getID()

                self.__log(
                    LOG_WARN,
                    f"(client ID {client_id}) Authentication error (received invalid session credentials)",
                )

        except Exception as E:
            if self.access_token_manager:
                self.access_token_manager.closeDatabase()

            self.__log(
                LOG_ERROR, f"An error occured during server initialization : {E}"
            )

            raise E

    def startProcess(self):
        self.__log(LOG_INFO, "Starting server ...")
        signal.signal(signal.SIGTERM, self.stopProcess)
        signal.signal(signal.SIGINT, self.stopProcess)

        if self.config_content["log_rotation"].get("enabled"):
            self.is_running = True
            threading.Thread(target=self.__log_rotate_routine).start()

        self.server_interface.startServer()

    # 2 parameters are given on method call ?
    # Probably missing info here
    def stopProcess(self, n=None, p=None):
        self.__log(LOG_INFO, "Stopping server ...")
        if self.access_token_manager:
            self.access_token_manager.closeDatabase()

        if self.config_content["log_rotation"].get("enabled"):
            self.is_running = False

        if self.server_interface:
            self.server_interface.stopServer()


def launchServerProcess(
    config_content,
    enable_stdout_log=DEFAULT_ENABLE_STDOUT_LOG,
    enable_traceback_on_log=DEFAULT_ENABLE_TRACEBACK_ON_LOG,
):
    process = AnweddolServerProcess(
        config_content,
        enable_stdout_log=enable_stdout_log,
        enable_traceback_on_log=enable_traceback_on_log,
    )

    try:
        process.initializeProcess()
        process.startProcess()

    except Exception as E:
        process.stopProcess()
        raise E
