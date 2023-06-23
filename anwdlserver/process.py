"""
    Copyright 2023 The Anweddol project
    See the LICENSE file for licensing informations
    ---

    CLI : Main server process functions

"""
import logging
import getpass
import signal
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


def launchServerProcess(config_content):
    runtime_rsa_wrapper = None

    if not config_content["server"].get("enable_onetime_rsa_keys"):
        if not os.path.exists(config_content["paths"].get("rsa_keys_root_path")):
            os.mkdir(config_content["paths"].get("rsa_keys_root_path"))

        if not os.path.exists(
            config_content["paths"].get("rsa_keys_root_path")
            + "/"
            + PRIVATE_PEM_KEY_FILENAME
        ):
            runtime_rsa_wrapper = RSAWrapper()

            with open(
                config_content["paths"].get("rsa_keys_root_path")
                + "/"
                + PUBLIC_PEM_KEY_FILENAME,
                "w",
            ) as fd:
                fd.write(runtime_rsa_wrapper.getPublicKey().decode())

            with open(
                config_content["paths"].get("rsa_keys_root_path")
                + "/"
                + PRIVATE_PEM_KEY_FILENAME,
                "w",
            ) as fd:
                fd.write(runtime_rsa_wrapper.getPrivateKey().decode())

        else:
            runtime_rsa_wrapper = RSAWrapper(generate_key_pair=False)

            with open(
                config_content["paths"].get("rsa_keys_root_path")
                + "/"
                + PUBLIC_PEM_KEY_FILENAME,
                "r",
            ) as fd:
                runtime_rsa_wrapper.setPublicKey(fd.read().encode())

            with open(
                config_content["paths"].get("rsa_keys_root_path")
                + "/"
                + PRIVATE_PEM_KEY_FILENAME,
                "r",
            ) as fd:
                runtime_rsa_wrapper.setPrivateKey(fd.read().encode())

    server_interface = ServerInterface(
        bind_address=config_content["server"].get("bind_address"),
        listen_port=config_content["server"].get("listen_port"),
        client_timeout=config_content["server"].get("timeout"),
        runtime_virtualization_interface=VirtualizationInterface(
            config_content["paths"].get("container_iso_path"),
            max_allowed_containers=config_content["container"].get(
                "max_allowed_running_containers"
            ),
        ),
        runtime_rsa_wrapper=runtime_rsa_wrapper,
    )

    logging.basicConfig(
        format="%(asctime)s %(levelname)s : %(message)s",
        filename=config_content["paths"].get("log_file_path"),
        level=logging.INFO,
        encoding="utf-8",
        filemode="a",
    )

    if config_content["access_token"].get("enabled"):
        access_token_manager = AccessTokenManager(
            config_content["paths"].get("access_tokens_database_path")
        )

    @server_interface.on_created_container
    def handle_container_creation(**kwargs):
        container_instance = kwargs.get("container_instance")

        logging.info(
            f"[{kwargs['client_instance'].getID()}] Container {kwargs['container_instance'].getUUID()} was created"
        )

        container_instance.setMemory(
            config_content["container"].get("container_memory")
        )
        container_instance.setVCPUs(config_content["container"].get("container_vcpus"))
        container_instance.setNATInterfaceName(
            config_content["container"].get("nat_interface_name")
        )
        container_instance.setBridgeInterfaceName(
            config_content["container"].get("bridge_interface_name")
        )
        container_instance.setEndpointSSHAuthenticationCredentials(
            config_content["container"].get("endpoint_username"),
            config_content["container"].get("endpoint_password"),
            config_content["container"].get("endpoint_listen_port"),
        )
        container_instance.startDomain()

        logging.info(
            f"[{kwargs['client_instance'].getID()}] Container {kwargs['container_instance'].getUUID()} domain is started"
        )

    @server_interface.on_connection
    def handle_new_connection(**kwargs):
        if config_content["ip_filter"].get("enabled"):
            client_socket = kwargs.get("client_socket")

            if "any" in config_content["ip_filter"].get("denied_ip_list"):
                if client_socket.getpeername()[0] not in config_content[
                    "ip_filter"
                ].get("allowed_ip_list") and "any" not in config_content[
                    "ip_filter"
                ].get(
                    "allowed_ip_list"
                ):
                    client_socket.shutdown(2)
                    client_socket.close()
                    logging.error(
                        f"[unspec] Denied ip : {client_socket.getpeername()[0]} (IP not allowed)"
                    )

            if client_socket.getpeername()[0] in config_content["ip_filter"].get(
                "denied_ip_list"
            ):
                client_socket.shutdown(2)
                client_socket.close()
                logging.error(
                    f"[unspec] Denied ip : {client_socket.getpeername()[0]} (Denied IP)"
                )

            logging.info("[unspec] IP allowed")

    @server_interface.on_client
    def handle_new_client(**kwargs):
        client_instance = kwargs.get("client_instance")

        logging.info(f"[{client_instance.getID()}] New client connected")

    @server_interface.on_request
    def handle_request(**kwargs):
        client_instance = kwargs["client_instance"]
        request_verb = client_instance.getStoredRequest()["verb"]

        logging.info(
            f"[{kwargs['client_instance'].getID()}] Received {request_verb} request"
        )

        if config_content.get("access_token").get("enabled"):
            client_request = client_instance.getStoredRequest()

            if not client_request["parameters"].get("access_token"):
                client_instance.sendResponse(
                    False,
                    RESPONSE_MSG_BAD_REQ,
                    reason="Access token is required",
                )
                client_instance.closeConnection()
                logging.error(
                    f"[{client_instance.getID()}] Authorization failed (No access token provided)"
                )
                return

            if not access_token_manager.getEntryID(
                client_request["parameters"].get("access_token")
            ):
                client_instance.sendResponse(
                    False, RESPONSE_MSG_BAD_AUTH, reason="Invalid access token"
                )
                client_instance.closeConnection()
                logging.error(
                    f"[{client_instance.getID()}] Authorization failed (Invalid access token)"
                )
                return

            logging.info(f"[{client_instance.getID()}] Authorization success")

    @server_interface.on_stopped
    def handle_stopped(**kwargs):
        logging.info("Server is stopped")

        if config_content["access_token"].get("enabled"):
            access_token_manager.closeDatabase()

    @server_interface.on_started
    def notify_started(**kwargs):
        logging.info("Server is started")
        logging.info(f"Running as {getpass.getuser()}")

    @server_interface.on_created_endpoint_shell
    def notify_endpoint_shell_creation(**kwargs):
        logging.info(f"[{kwargs.get('client_instance').getID()}] Endpoint shell opened")

    @server_interface.on_destroyed_container
    def notify_destroyed_container(**kwargs):
        logging.info(
            f"[{kwargs.get('client_instance').getID()}] Container {kwargs.get('container_instance').getUUID()} was destroyed"
        )

    @server_interface.on_client_closed
    def notify_client_closed(**kwargs):
        logging.info(f"[{kwargs.get('client_instance').getID()}] Connection closed")

    @server_interface.on_malformed_request
    def notify_malformed_request(**kwargs):
        logging.error(
            f"[{kwargs.get('client_instance').getID()}] Received malformed request"
        )

    @server_interface.on_unknown_verb
    def notify_unknown_verb(**kwargs):
        verb = kwargs.get("client_instance").getStoredRequest()["verb"]
        logging.error(
            f"[{kwargs.get('client_instance').getID()}] Received unknown verb : '{verb}'"
        )

    @server_interface.on_runtime_error
    def notify_runtime_error(**kwargs):
        logging.error(
            "[{}] {} : {}".format(
                kwargs["client_instance"].getID()
                if kwargs.get("client_instance")
                else "unspec",
                type(kwargs.get("ex_class")),
                kwargs.get("ex_class"),
            )
        )

    def _start():
        logging.warning("Starting server ...")
        server_interface.startServer()

    # 2 parameters are given on method call ?
    # Probably missing info here
    def _stop(n=None, p=None):
        logging.warning("Stopping server ...")
        server_interface.stopServer()

    signal.signal(signal.SIGTERM, _stop)
    signal.signal(signal.SIGINT, _stop)

    _start()
