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
)
from .core.virtualization import VirtualizationInterface
from .core.crypto import RSAWrapper
from .tools.accesstk import AccessTokenManager


# Constants definition
PUBLIC_PEM_KEY_FILENAME = "public_key.pem"
PRIVATE_PEM_KEY_FILENAME = "private_key.pem"


class AnweddolServerCLIProcess:
    def __init__(self, config_content):
        self.config_content = config_content
        self.access_token_manager = None
        self.runtime_rsa_wrapper = None
        self.server_interface = None
        self.is_running = False

    def __log_rotate_routine(self):
        while self.is_running:
            with open(self.config_content["server"].get("log_file_path"), "r") as fd:
                if len([0 for line in fd.readlines()]) >= self.config_content[
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

    def initializeProcess(self):
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

        try:
            logging.warning(
                f"[INIT] Initializing server (running as '{getpass.getuser()}') ..."
            )

            logging.info("[INIT] Loading instance RSA key pair ...")
            if not self.config_content["server"].get("enable_onetime_rsa_keys"):
                if not os.path.exists(
                    self.config_content["server"].get("rsa_keys_root_path")
                ):
                    os.mkdir(self.config_content["server"].get("rsa_keys_root_path"))

                if not os.path.exists(
                    self.config_content["server"].get("rsa_keys_root_path")
                    + "/"
                    + PRIVATE_PEM_KEY_FILENAME
                ):
                    self.runtime_rsa_wrapper = RSAWrapper()

                    with open(
                        self.config_content["server"].get("rsa_keys_root_path")
                        + "/"
                        + PUBLIC_PEM_KEY_FILENAME,
                        "w",
                    ) as fd:
                        fd.write(self.runtime_rsa_wrapper.getPublicKey().decode())

                    with open(
                        self.config_content["server"].get("rsa_keys_root_path")
                        + "/"
                        + PRIVATE_PEM_KEY_FILENAME,
                        "w",
                    ) as fd:
                        fd.write(self.runtime_rsa_wrapper.getPrivateKey().decode())

                else:
                    self.runtime_rsa_wrapper = RSAWrapper(generate_key_pair=False)

                    with open(
                        self.config_content["server"].get("rsa_keys_root_path")
                        + "/"
                        + PUBLIC_PEM_KEY_FILENAME,
                        "r",
                    ) as fd:
                        self.runtime_rsa_wrapper.setPublicKey(fd.read().encode())

                    with open(
                        self.config_content["server"].get("rsa_keys_root_path")
                        + "/"
                        + PRIVATE_PEM_KEY_FILENAME,
                        "r",
                    ) as fd:
                        self.runtime_rsa_wrapper.setPrivateKey(fd.read().encode())

            logging.info("[INIT] Initializing server interface ...")
            self.server_interface = ServerInterface(
                bind_address=self.config_content["server"].get("bind_address"),
                listen_port=self.config_content["server"].get("listen_port"),
                client_timeout=self.config_content["server"].get("timeout"),
                runtime_virtualization_interface=VirtualizationInterface(
                    self.config_content["container"].get("container_iso_path"),
                    max_allowed_containers=self.config_content["container"].get(
                        "max_allowed_running_containers"
                    ),
                ),
                runtime_rsa_wrapper=self.runtime_rsa_wrapper,
            )

            if self.config_content["access_token"].get("enabled"):
                logging.info("[INIT] Loading access token database ...")
                self.access_token_manager = AccessTokenManager(
                    self.config_content["container"].get("access_tokens_database_path")
                )

            logging.info("[INIT] Binding handlers routine ...")

            @self.server_interface.on_created_container
            def handle_container_creation(**kwargs):
                container_instance = kwargs.get("container_instance")

                logging.info(
                    f"(client ID {kwargs['client_instance'].getID()}) Container {kwargs['container_instance'].getUUID()} was created"
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
                container_instance.setBridgeInterfaceName(
                    self.config_content["container"].get("bridge_interface_name")
                )
                container_instance.setEndpointSSHAuthenticationCredentials(
                    self.config_content["container"].get("endpoint_username"),
                    self.config_content["container"].get("endpoint_password"),
                    self.config_content["container"].get("endpoint_listen_port"),
                )
                container_instance.startDomain()

                logging.info(
                    f"(client ID {kwargs['client_instance'].getID()}) Container {kwargs['container_instance'].getUUID()} domain is started"
                )

            @self.server_interface.on_connection
            def handle_new_connection(**kwargs):
                if self.config_content["ip_filter"].get("enabled"):
                    client_socket = kwargs.get("client_socket")

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
                            logging.error(
                                f"(unspec) Denied ip : {client_socket.getpeername()[0]} (IP not allowed)"
                            )

                    if client_socket.getpeername()[0] in self.config_content[
                        "ip_filter"
                    ].get("denied_ip_list"):
                        client_socket.shutdown(2)
                        client_socket.close()
                        logging.error(
                            f"(unspec) Denied ip : {client_socket.getpeername()[0]} (Denied IP)"
                        )

                    logging.info("(unspec) IP allowed")

            @self.server_interface.on_client
            def handle_new_client(**kwargs):
                client_instance = kwargs.get("client_instance")

                logging.info(
                    f"(client ID {client_instance.getID()}) New client connected"
                )

            @self.server_interface.on_request
            def handle_request(**kwargs):
                client_instance = kwargs["client_instance"]
                request_verb = client_instance.getStoredRequest()["verb"]

                logging.info(
                    f"(client ID {kwargs['client_instance'].getID()}) Received {request_verb} request"
                )

                if self.config_content.get("access_token").get("enabled"):
                    client_request = client_instance.getStoredRequest()

                    if not client_request["parameters"].get("access_token"):
                        client_instance.sendResponse(
                            False,
                            RESPONSE_MSG_BAD_REQ,
                            reason="Access token is required",
                        )
                        client_instance.closeConnection()
                        logging.error(
                            f"(client ID {client_instance.getID()}) Authorization failed (No access token provided)"
                        )
                        return -1

                    if not self.access_token_manager.getEntryID(
                        client_request["parameters"].get("access_token")
                    ):
                        client_instance.sendResponse(
                            False, RESPONSE_MSG_BAD_AUTH, reason="Invalid access token"
                        )
                        client_instance.closeConnection()
                        logging.error(
                            f"(client ID {client_instance.getID()}) Authorization failed (Invalid access token)"
                        )
                        return -1

                    logging.info(
                        f"(client ID {client_instance.getID()}) Authorization success"
                    )

            @self.server_interface.on_stopped
            def handle_stopped(**kwargs):
                logging.info("Server is stopped")

                if self.config_content["access_token"].get("enabled"):
                    self.access_token_manager.closeDatabase()

            @self.server_interface.on_started
            def notify_started(**kwargs):
                logging.info("Server is started")

            @self.server_interface.on_created_endpoint_shell
            def notify_endpoint_shell_creation(**kwargs):
                logging.info(
                    f"(client ID {kwargs.get('client_instance').getID()}) Endpoint shell opened"
                )

            @self.server_interface.on_destroyed_container
            def notify_destroyed_container(**kwargs):
                logging.info(
                    f"(client ID {kwargs.get('client_instance').getID()}) Container {kwargs.get('container_instance').getUUID()} was destroyed"
                )

            @self.server_interface.on_client_closed
            def notify_client_closed(**kwargs):
                logging.info(
                    f"(client ID {kwargs.get('client_instance').getID()}) Connection closed"
                )

            @self.server_interface.on_malformed_request
            def notify_malformed_request(**kwargs):
                logging.error(
                    f"(client ID {kwargs.get('client_instance').getID()}) Received malformed request"
                )

            @self.server_interface.on_unknown_verb
            def notify_unknown_verb(**kwargs):
                verb = kwargs.get("client_instance").getStoredRequest()["verb"]
                logging.error(
                    f"(client ID {kwargs.get('client_instance').getID()}) Received unknown verb : '{verb}'"
                )

            @self.server_interface.on_runtime_error
            def notify_runtime_error(**kwargs):
                logging.error(
                    "(client ID {}) {} : {}".format(
                        kwargs["client_instance"].getID()
                        if kwargs.get("client_instance")
                        else "unspec",
                        type(kwargs.get("ex_class")),
                        kwargs.get("ex_class"),
                    )
                )

            logging.info("[INIT] All done. Server is ready to use")

        except Exception as E:
            if self.access_token_manager:
                self.access_token_manager.closeDatabase()

            logging.error(f"[INIT] An error occured during server initialization : {E}")
            return -1

    def startProcess(self):
        logging.info("Starting server ...")
        signal.signal(signal.SIGTERM, self.stopProcess)
        signal.signal(signal.SIGINT, self.stopProcess)

        if self.config_content["log_rotation"].get("enabled"):
            self.is_running = True
            threading.Thread(target=self.__log_rotate_routine).start()

        self.server_interface.startServer()

    # 2 parameters are given on method call ?
    # Probably missing info here
    def stopProcess(self, n=None, p=None):
        logging.info("Stopping server ...")
        if self.access_token_manager:
            self.access_token_manager.closeDatabase()

        if self.config_content["log_rotation"].get("enabled"):
            self.is_running = False

        self.server_interface.stopServer()


def launchServerProcess(config_content):
    process = AnweddolServerCLIProcess(config_content)

    try:
        process.initializeProcess()
        process.startProcess()

    except KeyboardInterrupt:
        process.stopProcess()
