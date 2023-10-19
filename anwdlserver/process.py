"""
Copyright 2023 The Anweddol project
See the LICENSE file for licensing informations
---

This module defines the 'anwdlserver' CLI executable server process.

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
from .web.server import WebServerInterface
from .core.crypto import RSAWrapper

from .tools.access_token import AccessTokenManager
from .utilities import createFileRecursively
from .__init__ import __version__

# Constants definition
LOG_INFO = "INFO: "
LOG_WARN = "WARNING: "
LOG_ERROR = "ERROR: "

SERVER_TYPE_CLASSIC = 1
SERVER_TYPE_WEB = 2

# Default parameters
DEFAULT_ENABLE_STDOUT_LOG = False
DEFAULT_ENABLE_TRACEBACK_ON_LOG = False
DEFAULT_DISABLE_LOGGING = False


class AnweddolServerProcess:
    def __init__(
        self,
        server_type,
        config_content,
        enable_stdout_log=DEFAULT_ENABLE_STDOUT_LOG,
        enable_traceback_on_log=DEFAULT_ENABLE_TRACEBACK_ON_LOG,
        disable_logging=DEFAULT_DISABLE_LOGGING,
    ):
        self.enable_stdout_log = enable_stdout_log
        self.enable_traceback_on_log = enable_traceback_on_log

        self.disable_logging = disable_logging
        self.config_content = config_content
        self.access_token_manager = None
        self.runtime_rsa_wrapper = None
        self.server_type = server_type
        self.server_interface = None
        self.is_running = False

        self.actual_running_container_domains_counter = 0

        if not self.disable_logging:
            logging.basicConfig(
                format="%(asctime)s %(levelname)s : %(message)s",
                filename=self.config_content["server"].get("log_file_path"),
                level=logging.INFO,
                encoding="utf-8",
                filemode="a",
            )

        try:
            container_iso_file_path = self.config_content["container"].get(
                "container_iso_file_path"
            )
            bind_address = self.config_content["server"].get("bind_address")
            listen_port = self.config_content[
                "server" if self.server_type == SERVER_TYPE_CLASSIC else "web_server"
            ].get("listen_port")
            timeout = self.config_content["server"].get("timeout")

            self._log(
                LOG_WARN,
                f"Initializing server (running as '{getpass.getuser()}') ...",
            )

            if self.server_type == SERVER_TYPE_CLASSIC:
                self._log(LOG_INFO, "Loading instance RSA key pair ...")

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
                                fd.write(
                                    self.runtime_rsa_wrapper.getPublicKey().decode()
                                )

                        else:
                            with open(public_key_path, "r") as fd:
                                self.runtime_rsa_wrapper.setPublicKey(
                                    fd.read().encode()
                                )

            self._log(LOG_INFO, "Initializing server interface ...")

            self.server_interface = (
                ServerInterface(
                    container_iso_file_path,
                    bind_address=bind_address,
                    listen_port=listen_port,
                    client_timeout=timeout,
                    runtime_rsa_wrapper=self.runtime_rsa_wrapper,
                )
                if self.server_type == SERVER_TYPE_CLASSIC
                else WebServerInterface(
                    container_iso_file_path,
                    listen_port=listen_port,
                )
            )

            if self.config_content["access_token"].get("enabled"):
                self._log(LOG_INFO, "Loading access token database ...")

                self.access_token_manager = AccessTokenManager(
                    self.config_content["access_token"].get(
                        "access_token_database_file_path"
                    )
                )

            self._log(LOG_INFO, "Binding handlers routine ...")

            def handle_stat_request(**kwargs):  # A voir si web server
                client_instance = kwargs.get("client_instance")
                client_id = kwargs.get("client_instance").getID()

                try:
                    _, _, uptime = self.server_interface.getRuntimeStatistics()
                    max_allowed_running_container_domains = self.config_content[
                        "container"
                    ].get("max_allowed_running_container_domains")

                    client_instance.sendResponse(
                        True,
                        RESPONSE_MSG_OK,
                        data={
                            "version": __version__,
                            "uptime": uptime,
                            "available": (
                                max_allowed_running_container_domains
                                - self.actual_running_container_domains_counter
                            )
                            if max_allowed_running_container_domains
                            else "nolimit",
                        },
                    )
                    client_instance.closeConnection()

                    self._log(LOG_INFO, f"(client ID {client_id}) Connection closed")

                except Exception as E:
                    client_instance.sendResponse(False, RESPONSE_MSG_INTERNAL_ERROR)
                    client_instance.closeConnection()

                    self._log(LOG_INFO, f"(client ID {client_id}) Connection closed")

                    raise E

            self.server_interface.setRequestHandler(
                REQUEST_VERB_STAT, handle_stat_request
            )

            # Decorators specified in the condition statements are only used
            # on a classic server instance
            if self.server_type == SERVER_TYPE_CLASSIC:

                @self.server_interface.on_connection_accepted
                def handle_new_connection(context, data):
                    if not self.config_content["ip_filter"].get("enabled"):
                        return

                    client_socket = data.get("client_socket")
                    client_ip, _ = client_socket.getpeername()

                    allowed_ip_list = self.config_content["ip_filter"].get(
                        "allowed_ip_list"
                    )
                    denied_ip_list = self.config_content["ip_filter"].get(
                        "denied_ip_list"
                    )

                    if "any" in denied_ip_list:
                        if (
                            client_ip not in allowed_ip_list
                            and "any" not in allowed_ip_list
                        ):
                            client_socket.shutdown(2)
                            client_socket.close()

                            self._log(
                                LOG_WARN,
                                f"(unspec) Denied ip : {client_ip} (IP not allowed)",
                            )

                            return

                    if client_ip in denied_ip_list:
                        client_socket.shutdown(2)
                        client_socket.close()

                        self._log(
                            LOG_WARN,
                            f"(unspec) Denied ip : {client_ip} (Denied IP)",
                        )

                        return

                    self._log(LOG_INFO, "(unspec) IP allowed")

                @self.server_interface.on_client_initialized
                def handle_new_client(context, data):
                    client_id = data.get("client_instance").getID()

                    self._log(LOG_INFO, f"(client ID {client_id}) New client connected")

                @self.server_interface.on_client_closed
                def notify_client_closed(context, data):
                    client_id = data.get("client_instance").getID()

                    self._log(LOG_INFO, f"(client ID {client_id}) Connection closed")

            @self.server_interface.on_container_created
            def handle_container_creation(context, data):
                container_instance = data.get("container_instance")
                client_id = data.get("client_instance").getID()

                max_allowed_running_container_domains = self.config_content[
                    "container"
                ].get("max_allowed_running_container_domains")

                self._log(
                    LOG_INFO,
                    f"(client ID {client_id}) Container {container_instance.getUUID()} was created",
                )
                self._log(
                    LOG_INFO,
                    "(client ID {}) Actual running container domains amount : {} / {}".format(
                        client_id,
                        self.actual_running_container_domains_counter,
                        max_allowed_running_container_domains,
                    ),
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

            @self.server_interface.on_request
            def handle_request(context, data):  # Change avec type de serveur
                if self.server_type == SERVER_TYPE_CLASSIC:
                    client_instance = data.get("client_instance")
                    client_id = data.get("client_instance").getID()

                    client_request = client_instance.getStoredRequest()
                    request_verb = client_instance.getStoredRequest().get("verb")

                    self._log(
                        LOG_INFO,
                        f"(client ID {client_id}) Received {request_verb} request",
                    )

                    if self.config_content.get("access_token").get("enabled"):
                        if not client_request["parameters"].get("access_token"):
                            client_instance.sendResponse(
                                False,
                                RESPONSE_MSG_BAD_REQ,
                                reason="Access token is required",
                            )
                            self._log(
                                LOG_WARN,
                                f"(client ID {client_id}) Access authentication failed (No access token provided)",
                            )

                            client_instance.closeConnection()

                            self._log(
                                LOG_INFO, f"(client ID {client_id}) Connection closed"
                            )

                            return

                        if not self.access_token_manager.getEntryID(
                            client_request["parameters"].get("access_token")
                        ):
                            client_instance.sendResponse(
                                False,
                                RESPONSE_MSG_BAD_AUTH,
                                reason="Invalid access token",
                            )
                            self._log(
                                LOG_WARN,
                                f"(client ID {client_id}) Access authentication failed (Invalid access token)",
                            )

                            client_instance.closeConnection()

                            self._log(
                                LOG_INFO, f"(client ID {client_id}) Connection closed"
                            )

                            return

                        self._log(
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
                        self._log(
                            LOG_WARN,
                            f"(client ID {client_id}) Maximum allowed amount of running containers has been reached",
                        )

                        client_instance.closeConnection()
                        self._log(
                            LOG_INFO, f"(client ID {client_id}) Connection closed"
                        )

                else:
                    pass

            @self.server_interface.on_server_stopped
            def handle_server_stopped(context, data):
                self._log(LOG_INFO, "Server is stopped")

                if self.config_content["access_token"].get("enabled"):
                    self.access_token_manager.closeDatabase()

            @self.server_interface.on_server_started
            def notify_started(context, data):
                self._log(LOG_INFO, "Server is started")

            @self.server_interface.on_endpoint_shell_created
            def handle_endpoint_shell_creation(context, data):
                client_id = data.get("client_instance").getID()
                endpoint_shell_instance = data.get("endpoint_shell_instance")

                endpoint_shell_instance.setEndpointCredentials(
                    self.config_content["container"].get("endpoint_username"),
                    self.config_content["container"].get("endpoint_password"),
                    self.config_content["container"].get("endpoint_listen_port"),
                )

                self._log(LOG_INFO, f"(client ID {client_id}) Endpoint shell created")

            @self.server_interface.on_malformed_request
            def notify_malformed_request(context, data):
                client_id = data.get("client_instance").getID()

                self._log(
                    LOG_WARN, f"(client ID {client_id}) Received malformed request"
                )

            @self.server_interface.on_unhandled_verb
            def notify_unhandled_verb(context, data):
                verb = data.get("client_instance").getStoredRequest()["verb"]
                client_id = data.get("client_instance").getID()

                self._log(
                    LOG_WARN,
                    f"(client ID {client_id}) Received unhandled verb : '{verb}'",
                )

            @self.server_interface.on_container_domain_started
            def notify_container_domain_started(context, data):
                container_uuid = data.get("container_instance").getUUID()
                container_ip = data.get("container_instance").getIP()
                client_id = data.get("client_instance").getID()

                self.actual_running_container_domains_counter += 1

                self._log(
                    LOG_INFO,
                    f"(client ID {client_id}) Container {container_uuid} domain is running",
                )
                self._log(
                    LOG_INFO,
                    f"(client ID {client_id}) Container IP : {container_ip}",
                )

            @self.server_interface.on_container_domain_stopped
            def notify_container_domain_stopped(context, data):
                container_uuid = data.get("container_instance").getUUID()
                client_id = (
                    data.get("client_instance").getID()
                    if data.get("client_instance")
                    else "unspec"
                )

                if self.actual_running_container_domains_counter > 0:
                    self.actual_running_container_domains_counter -= 1

                self._log(
                    LOG_INFO,
                    f"(client ID {client_id}) Container {container_uuid} domain was stopped",
                )

            @self.server_interface.on_endpoint_shell_closed
            def notify_endpoint_shell_closed(context, data):
                client_id = data.get("client_instance").getID()

                self._log(
                    LOG_INFO, f"(client ID {client_id}) Endpoint shell was closed"
                )

            @self.server_interface.on_runtime_error
            def notify_runtime_error(context, data):
                client_id = (
                    data.get("client_instance").getID()
                    if data.get("client_instance")
                    else "unspec"
                )
                exception_object = data.get("exception_object")

                self._log(
                    LOG_ERROR,
                    f"(client ID {client_id}) {type(exception_object)} : {exception_object}",
                )

                if self.enable_traceback_on_log:
                    traceback = data.get("traceback")
                    self._log(LOG_ERROR, f" -> {traceback}")

            @self.server_interface.on_authentication_error
            def notify_authentication_error(context, data):
                client_id = data.get("client_instance").getID()

                self._log(
                    LOG_WARN,
                    f"(client ID {client_id}) Authentication error (received invalid session credentials)",
                )

        except Exception as E:
            if self.access_token_manager:
                self.access_token_manager.closeDatabase()

            self._log(LOG_ERROR, f"An error occured during server initialization : {E}")

            raise E

    def _log(self, kind, message):
        if self.disable_logging:
            return

        if kind == LOG_INFO:
            logging.info(message)

        elif kind == LOG_WARN:
            logging.warning(message)

        else:
            logging.error(message)

        if self.enable_stdout_log:
            print(f"{datetime.datetime.now()} {kind} : {message}")

    def _log_rotation_routine(self):
        max_log_lines_amount = self.config_content["log_rotation"].get(
            "max_log_lines_amount"
        )
        log_archive_folder_path = self.config_content["log_rotation"].get(
            "log_archive_folder_path"
        )
        log_file_path = self.config_content[
            "server" if self.server_type == SERVER_TYPE_CLASSIC else "web_server"
        ].get("log_file_path")

        while self.is_running:
            with open(log_file_path, "r") as fd:
                log_lines_amount = sum(1 for line in fd.readlines())

            if log_lines_amount < max_log_lines_amount:
                continue

            if not os.path.exists(log_archive_folder_path):
                os.mkdir(log_archive_folder_path)

            if self.config_content["log_rotation"].get("action") == "archive":
                ZipFile(
                    log_archive_folder_path
                    + ("/" if log_archive_folder_path[-1] != "/" else "")
                    + f"archived_{datetime.datetime.now()}.zip",
                    "w",
                ).write(log_file_path)

            # Open the log file path in write mode to erase its content
            with open(log_file_path, "w") as fd:
                fd.close()

            time.sleep(1)

    def startProcess(self):
        self._log(LOG_INFO, "Starting server ...")
        signal.signal(signal.SIGTERM, self.stopProcess)
        signal.signal(signal.SIGINT, self.stopProcess)

        if self.config_content["log_rotation"].get("enabled"):
            self.is_running = True
            threading.Thread(target=self._log_rotation_routine).start()

        self.server_interface.startServer()

    # signal_no and stack_frame are dummy arguments for signal handler execution
    # See https://docs.python.org/3/library/signal.html#signal.signal
    def stopProcess(self, signal_no=None, stack_frame=None):
        self._log(LOG_INFO, "Stopping server ...")
        if self.access_token_manager:
            self.access_token_manager.closeDatabase()

        if self.config_content["log_rotation"].get("enabled"):
            self.is_running = False

        if self.server_interface:
            self.server_interface.stopServer(die_on_error=True)


def launchServerProcess(
    server_type,
    config_content,
    enable_stdout_log=DEFAULT_ENABLE_STDOUT_LOG,
    enable_traceback_on_log=DEFAULT_ENABLE_TRACEBACK_ON_LOG,
):
    process = AnweddolServerProcess(
        server_type,
        config_content,
        enable_stdout_log=enable_stdout_log,
        enable_traceback_on_log=enable_traceback_on_log,
    )

    try:
        process.startProcess()

    except Exception as E:
        process.stopProcess()
        raise E
