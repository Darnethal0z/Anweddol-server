"""
Copyright 2023 The Anweddol project
See the LICENSE file for licensing informations
---

This module defines the 'anwdlserver' CLI server process.

"""

import threading
import getpass
import hashlib
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
    RESPONSE_MSG_REFUSED_REQ,
    REQUEST_VERB_STAT,
    REQUEST_VERB_CREATE,
    EVENT_CONTAINER_DOMAIN_STARTED,
)
from .core.sanitization import makeResponse
from .web.server import WebServerInterface
from .core.crypto import RSAWrapper

from .tools.access_token import AccessTokenManager
from .utilities import createFileRecursively
from .logging import (
    AnweddolServerCLILoggingManager,
    LOG_INFO,
    LOG_WARN,
    LOG_ERROR,
)
from .__init__ import __version__


SERVER_TYPE_CLASSIC = 1
SERVER_TYPE_WEB = 2

IP_FILTER_ALLOWED = 0
IP_FILTER_NOT_ALLOWED = -1
IP_FILTER_DENIED = -2


class AnweddolServerCLIServerProcess:
    def __init__(
        self,
        server_type,
        config_content,
        enable_stdout_log=False,
        enable_traceback_on_log=False,
        disable_logging=False,
    ):
        self.enable_traceback_on_log = enable_traceback_on_log
        self.actual_running_container_domains_counter = 0
        self.config_content = config_content
        self.access_token_manager = None
        self.runtime_rsa_wrapper = None
        self.server_interface = None
        self.log_manager = None
        self.is_running = False

        self.server_type = server_type
        self.server_config_key_name = (
            "server" if server_type == SERVER_TYPE_CLASSIC else "web_server"
        )

        try:
            self.log_manager = (
                AnweddolServerCLILoggingManager(
                    self.config_content[self.server_config_key_name].get(
                        "log_file_path"
                    ),
                    enable_stdout_log=enable_stdout_log,
                )
                if not disable_logging
                else None
            )

            self._initialize()

        except Exception as E:
            self._log(LOG_ERROR, f"An error occured during server initialization : {E}")

            if self.access_token_manager:
                self.access_token_manager.closeDatabase()

            raise E

    def _initialize(self):
        self._log(
            LOG_WARN,
            f"Initializing server (running as '{getpass.getuser()}') ...",
        )
        self._log(
            LOG_INFO,
            f"Server type : {'classic' if self.server_type == SERVER_TYPE_CLASSIC else 'web'}",
        )

        container_iso_file_path = self.config_content["container"].get(
            "container_iso_file_path"
        )
        listen_port = self.config_content[self.server_config_key_name].get(
            "listen_port"
        )

        if self.server_type == SERVER_TYPE_CLASSIC:
            timeout = self.config_content["server"].get("timeout")
            bind_address = self.config_content["server"].get("bind_address")
            public_key_path = self.config_content["server"].get(
                "public_rsa_key_file_path"
            )
            private_key_path = self.config_content["server"].get(
                "private_rsa_key_file_path"
            )

            if not self.config_content["server"].get("enable_onetime_rsa_keys"):
                self._log(LOG_INFO, "Loading instance RSA key pair ...")

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

        self._log(LOG_INFO, "Initializing server interface ...")

        if self.server_type == SERVER_TYPE_CLASSIC:
            self.server_interface = ServerInterface(
                container_iso_file_path,
                bind_address=bind_address,
                listen_port=listen_port,
                client_timeout=timeout,
                runtime_rsa_wrapper=self.runtime_rsa_wrapper,
            )

        else:
            enable_ssl = self.config_content["web_server"].get("enable_ssl")
            ssl_pem_private_key_file_path = self.config_content["web_server"].get(
                "ssl_pem_private_key_file_path"
            )
            ssl_pem_certificate_file_path = self.config_content["web_server"].get(
                "ssl_pem_certificate_file_path"
            )

            self.server_interface = WebServerInterface(
                container_iso_file_path,
                listen_port=listen_port,
                enable_ssl=enable_ssl,
                ssl_pem_private_key_file_path=ssl_pem_private_key_file_path,
                ssl_pem_certificate_file_path=ssl_pem_certificate_file_path,
            )

        if self.config_content["access_token"].get("enabled"):
            self._log(LOG_INFO, "Loading access token database ...")

            self.access_token_manager = AccessTokenManager(
                self.config_content["access_token"].get(
                    "access_token_database_file_path"
                )
            )

        self._log(LOG_INFO, "Binding handlers routine ...")

        def handle_stat_request(**kwargs):
            _, _, uptime = self.server_interface.getRuntimeStatistics()
            max_allowed_running_container_domains = self.config_content[
                "container"
            ].get("max_allowed_running_container_domains")

            response_data = {
                "version": __version__,
                "uptime": uptime,
                "available": (
                    max_allowed_running_container_domains
                    - self.actual_running_container_domains_counter
                )
                if max_allowed_running_container_domains
                else "nolimit",
            }

            if self.server_type == SERVER_TYPE_CLASSIC:
                client_instance = kwargs.get("client_instance")
                client_id = client_instance.getID()

                client_instance.sendResponse(
                    True,
                    RESPONSE_MSG_OK,
                    data=response_data,
                )
                client_instance.closeConnection()

                self._log(LOG_INFO, f"(client ID {client_id}) Connection closed")

            else:
                client_id = self._make_client_id(
                    kwargs.get("request_object").getClientIP()
                )

                return makeResponse(
                    True,
                    RESPONSE_MSG_OK,
                    data=response_data,
                )[1]

        self.server_interface.setRequestHandler(REQUEST_VERB_STAT, handle_stat_request)

        if self.server_type == SERVER_TYPE_CLASSIC:

            @self.server_interface.on_connection_accepted
            def handle_new_connection(context, data):
                if not self.config_content["ip_filter"].get("enabled"):
                    return

                client_socket = data.get("client_socket")
                client_ip, _ = client_socket.getpeername()

                client_id = self._make_client_id(client_ip)
                ip_filter_result = self._handle_ip_filter(client_ip)

                if ip_filter_result == IP_FILTER_NOT_ALLOWED:
                    self._log(
                        LOG_WARN,
                        f"(client ID {client_id}) Denied IP : {client_ip} (IP not allowed)",
                    )

                    client_socket.shutdown(2)
                    client_socket.close()

                elif ip_filter_result == IP_FILTER_DENIED:
                    self._log(
                        LOG_WARN,
                        f"(client ID {client_id}) Denied IP : {client_ip} (Denied IP)",
                    )

                    client_socket.shutdown(2)
                    client_socket.close()

                else:
                    self._log(LOG_INFO, f"(client ID {client_id}) IP allowed")

            @self.server_interface.on_client_initialized
            def handle_new_client(context, data):
                client_id = data.get("client_instance").getID()

                self._log(LOG_INFO, f"(client ID {client_id}) New client connected")

            @self.server_interface.on_client_closed
            def notify_client_closed(context, data):
                client_id = data.get("client_instance").getID()

                self._log(LOG_INFO, f"(client ID {client_id}) Connection closed")

        @self.server_interface.on_container_domain_started
        def notify_container_domain_started(context, data):
            container_uuid = data.get("container_instance").getUUID()
            container_ip = data.get("container_instance").getIP()

            if self.server_type == SERVER_TYPE_CLASSIC:
                client_id = data.get("client_instance").getID()

            else:
                client_id = (
                    self._make_client_id(data.get("request_object").getClientIP())
                    if data.get("request_object")
                    else "unspec"
                )

            self.actual_running_container_domains_counter += 1

            self._log(
                LOG_INFO,
                f"(client ID {client_id}) Container {container_uuid} domain is running",
            )
            self._log(
                LOG_INFO,
                f"(client ID {client_id}) Container IP : {container_ip}",
            )

        @self.server_interface.on_container_created
        def handle_container_creation(context, data):
            container_instance = data.get("container_instance")
            client_id = (
                data.get("client_instance").getID()
                if self.server_type == SERVER_TYPE_CLASSIC
                else self._make_client_id(data.get("request_object").getClientIP())
            )
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

            container_instance.startDomain(
                domain_type=self.config_content["container"].get("domain_type"),
                wait_max_tryout=self.config_content["container"].get("wait_max_tryout"),
            )

            self.server_interface.triggerEvent(
                EVENT_CONTAINER_DOMAIN_STARTED, context, data
            )

        @self.server_interface.on_request
        def handle_request(context, data):
            if self.server_type == SERVER_TYPE_CLASSIC:
                client_instance = data.get("client_instance")
                client_id = client_instance.getID()

                if not data.get("is_request_valid"):
                    return  # A malformed request response will be sent

                client_request = data.get("request_content")
                request_verb = client_request.get("verb")

            else:
                client_request = data.get("request_dict")
                request_object = data.get("request_object")
                request_verb = client_request.get("verb")

                client_id = self._make_client_id(request_object.getClientIP())

            if self.server_type == SERVER_TYPE_WEB and self.config_content[
                "ip_filter"
            ].get("enabled"):
                client_ip = request_object.getClientIP()

                ip_filter_result = self._handle_ip_filter(client_ip)

                if ip_filter_result == IP_FILTER_NOT_ALLOWED:
                    self._log(
                        LOG_WARN,
                        f"(client ID {client_id}) Denied IP : {client_ip} (IP not allowed)",
                    )

                    return makeResponse(False, RESPONSE_MSG_REFUSED_REQ)[1]

                elif ip_filter_result == IP_FILTER_DENIED:
                    self._log(
                        LOG_WARN,
                        f"(client ID {client_id}) Denied IP : {client_ip} (Denied IP)",
                    )

                    return makeResponse(False, RESPONSE_MSG_REFUSED_REQ)[1]

                else:
                    self._log(LOG_INFO, f"(client ID {client_id}) IP allowed")

            self._log(
                LOG_INFO,
                f"(client ID {client_id}) Received {request_verb if request_verb and self.server_type != SERVER_TYPE_WEB else 'home'} request",
            )

            if self.config_content.get("access_token").get("enabled"):
                if not client_request["parameters"].get("access_token"):
                    self._log(
                        LOG_WARN,
                        f"(client ID {client_id}) Access authentication failed (No access token provided)",
                    )

                    if self.server_type == SERVER_TYPE_CLASSIC:
                        client_instance.sendResponse(
                            False,
                            RESPONSE_MSG_BAD_REQ,
                            reason="Access token is required",
                        )

                        client_instance.closeConnection()

                        self._log(
                            LOG_INFO, f"(client ID {client_id}) Connection closed"
                        )

                        return

                    else:
                        return makeResponse(
                            False,
                            RESPONSE_MSG_BAD_REQ,
                            reason="Access token is required",
                        )[1]

                if not self.access_token_manager.getEntryID(
                    client_request["parameters"].get("access_token")
                ):
                    self._log(
                        LOG_WARN,
                        f"(client ID {client_id}) Access authentication failed (Invalid access token)",
                    )

                    if self.server_type == SERVER_TYPE_CLASSIC:
                        client_instance.sendResponse(
                            False,
                            RESPONSE_MSG_BAD_AUTH,
                            reason="Invalid access token",
                        )

                        client_instance.closeConnection()

                        self._log(
                            LOG_INFO, f"(client ID {client_id}) Connection closed"
                        )

                        return

                    else:
                        return makeResponse(
                            False,
                            RESPONSE_MSG_BAD_AUTH,
                            reason="Invalid access token",
                        )[1]

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
                self._log(
                    LOG_WARN,
                    f"(client ID {client_id}) Maximum allowed amount of running containers has been reached",
                )

                if self.server_type == SERVER_TYPE_CLASSIC:
                    client_instance.sendResponse(
                        False,
                        RESPONSE_MSG_UNAVAILABLE,
                        reason="The maximum allowed amount of running containers has been reached on the server",
                    )

                    client_instance.closeConnection()

                    self._log(LOG_INFO, f"(client ID {client_id}) Connection closed")

                else:
                    return makeResponse(
                        False,
                        RESPONSE_MSG_UNAVAILABLE,
                        reason="The maximum allowed amount of running containers has been reached on the server",
                    )[1]

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
            client_id = (
                data.get("client_instance").getID()
                if self.server_type == SERVER_TYPE_CLASSIC
                else self._make_client_id(data.get("request_object").getClientIP())
            )
            endpoint_shell_instance = data.get("endpoint_shell_instance")

            endpoint_shell_instance.setEndpointCredentials(
                self.config_content["container"].get("endpoint_username"),
                self.config_content["container"].get("endpoint_password"),
                self.config_content["container"].get("endpoint_listen_port"),
            )

            self._log(LOG_INFO, f"(client ID {client_id}) Endpoint shell created")

        @self.server_interface.on_malformed_request
        def notify_malformed_request(context, data):
            client_id = (
                data.get("client_instance").getID()
                if self.server_type == SERVER_TYPE_CLASSIC
                else self._make_client_id(data.get("request_object").getClientIP())
            )

            self._log(LOG_WARN, f"(client ID {client_id}) Received malformed request")

        @self.server_interface.on_unhandled_verb
        def notify_unhandled_verb(context, data):
            if self.server_type == SERVER_TYPE_CLASSIC:
                client_instance = data.get("client_instance")

                verb = client_instance.getStoredRequest().get("verb")
                client_id = client_instance.getID()

            else:
                verb = data.get("request_dict").get("verb")
                client_id = self._make_client_id(
                    data.get("request_object").getClientIP()
                )

            self._log(
                LOG_WARN,
                f"(client ID {client_id}) Unhandled verb : '{verb}'",
            )

        @self.server_interface.on_container_domain_stopped
        def notify_container_domain_stopped(context, data):
            container_uuid = data.get("container_instance").getUUID()

            if self.server_type == SERVER_TYPE_CLASSIC:
                client_id = (
                    data.get("client_instance").getID()
                    if data.get("client_instance")
                    else "unspec"
                )

            else:
                client_id = (
                    self._make_client_id(data.get("request_object").getClientIP())
                    if data.get("request_object")
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
            client_id = (
                data.get("client_instance").getID()
                if self.server_type == SERVER_TYPE_CLASSIC
                else self._make_client_id(data.get("request_object").getClientIP())
            )

            self._log(LOG_INFO, f"(client ID {client_id}) Endpoint shell was closed")

        @self.server_interface.on_runtime_error
        def notify_runtime_error(context, data):
            if self.server_type == SERVER_TYPE_CLASSIC:
                client_id = (
                    data.get("client_instance").getID()
                    if data.get("client_instance")
                    else "unspec"
                )

            else:
                client_id = (
                    (
                        data.get("client_instance").getID()
                        if self.server_type == SERVER_TYPE_CLASSIC
                        else self._make_client_id(
                            data.get("request_object").getClientIP()
                        )
                    )
                    if data.get("request_object")
                    else "unspec"
                )

            exception_object = data.get("exception_object")
            exception_object_type = (
                type(exception_object) if exception_object else "Unspecified error type"
            )

            self._log(
                LOG_ERROR,
                f"(client ID {client_id}) {exception_object_type} : {exception_object}",
            )

            if self.enable_traceback_on_log:
                traceback = data.get("traceback")

                self._log(LOG_ERROR, f" -> {traceback}")

        @self.server_interface.on_authentication_error
        def notify_authentication_error(context, data):
            client_id = (
                data.get("client_instance").getID()
                if self.server_type == SERVER_TYPE_CLASSIC
                else self._make_client_id(data.get("request_object").getClientIP())
            )

            self._log(
                LOG_WARN,
                f"(client ID {client_id}) Authentication error (received invalid session credentials)",
            )

    def _handle_ip_filter(self, client_ip):
        allowed_ip_list = self.config_content["ip_filter"].get("allowed_ip_list")
        denied_ip_list = self.config_content["ip_filter"].get("denied_ip_list")

        if "any" in denied_ip_list and (
            client_ip not in allowed_ip_list and "any" not in allowed_ip_list
        ):
            return IP_FILTER_NOT_ALLOWED

        if client_ip in denied_ip_list:
            return IP_FILTER_DENIED

        return IP_FILTER_ALLOWED

    def _make_client_id(self, client_ip):
        return hashlib.sha256(client_ip.encode(), usedforsecurity=False).hexdigest()[:7]

    def _log(self, kind, message):
        if not self.log_manager:
            return

        self.log_manager.log(kind, message)

    def _log_rotation_routine(self):
        max_log_lines_amount = self.config_content["log_rotation"].get(
            "max_log_lines_amount"
        )
        log_archive_folder_path = self.config_content["log_rotation"].get(
            "log_archive_folder_path"
        )
        log_file_path = self.config_content[self.server_config_key_name].get(
            "log_file_path"
        )

        while self.is_running:
            with open(log_file_path, "r") as fd:
                log_lines_amount = sum(1 for line in fd.readlines())

            if log_lines_amount < max_log_lines_amount:
                continue

            if not os.path.exists(log_archive_folder_path):
                createFileRecursively(log_archive_folder_path, is_folder=True)

            self.log_manager.rotate(
                self.config_content["log_rotation"].get("action") == "archive",
                log_archive_folder_path=log_archive_folder_path,
            )

            time.sleep(1)

    def startProcess(self):
        self._log(LOG_INFO, "Starting server ...")

        signal.signal(signal.SIGTERM, self.stopProcess)
        signal.signal(signal.SIGINT, self.stopProcess)

        if self.config_content["log_rotation"].get("enabled") and self.log_manager:
            self.is_running = True
            threading.Thread(target=self._log_rotation_routine).start()

        self.server_interface.startServer()

    # signal_no and stack_frame are dummy arguments for signal handler execution
    # See https://docs.python.org/3/library/signal.html#signal.signal
    def stopProcess(self, signal_no=None, stack_frame=None):
        self._log(LOG_INFO, "Stopping server ...")

        if self.access_token_manager:
            self.access_token_manager.closeDatabase()

        if self.config_content["log_rotation"].get("enabled") and self.log_manager:
            self.is_running = False

        if self.server_interface:
            self.server_interface.stopServer(die_on_error=True)


def launchServerProcess(
    server_type,
    config_content,
    enable_stdout_log=False,
    enable_traceback_on_log=False,
):
    server_process = AnweddolServerCLIServerProcess(
        server_type,
        config_content,
        enable_stdout_log=enable_stdout_log,
        enable_traceback_on_log=enable_traceback_on_log,
    )

    try:
        server_process.startProcess()

    except Exception as E:
        server_process.stopProcess()
        raise E
