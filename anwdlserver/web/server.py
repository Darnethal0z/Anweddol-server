"""
Copyright 2023 The Anweddol project
See the LICENSE file for licensing informations
---

This module contains an HTTP alternative to the classic server. 
It consists of a REST API based on the ServerInterface class, which provides 
all the features of a classic server, but in the form of a web server.

The request / response scheme stays the same, except that they are exprimed
in the form of an URL : "http://<server:port>/<verb>".
The server responds by a JSON response containing a normalized response dictionary.

"""

from twisted.web.http import Request
from twisted.web import server, resource
from twisted.internet.error import ReactorNotRunning
from twisted.internet import reactor, task, defer, ssl, endpoints, threads
import threading
import json
import time
import os

from ..core.server import (
    ServerInterface,
    EVENT_SERVER_STARTED,
    EVENT_SERVER_STOPPED,
    EVENT_RUNTIME_ERROR,
    EVENT_REQUEST,
    EVENT_UNHANDLED_VERB,
    EVENT_MALFORMED_REQUEST,
    EVENT_CONTAINER_DOMAIN_STOPPED,
    CONTEXT_NORMAL_PROCESS,
    CONTEXT_ERROR,
    REQUEST_VERB_CREATE,
    REQUEST_VERB_DESTROY,
    REQUEST_VERB_STAT,
    RESPONSE_MSG_BAD_REQ,
    RESPONSE_MSG_INTERNAL_ERROR,
)
from ..core.virtualization import VirtualizationInterface
from ..core.database import DatabaseInterface
from ..core.port_forwarding import PortForwardingInterface
from ..core.sanitization import makeResponse, verifyRequestContent

# Default values
DEFAULT_RESTWEBSERVER_LISTEN_PORT = 8080
DEFAULT_ENABLE_SSL = False


class WebServerInterface(ServerInterface, resource.Resource):
    isLeaf = True

    def __init__(
        self,
        runtime_container_iso_file_path: str,
        listen_port: int = DEFAULT_RESTWEBSERVER_LISTEN_PORT,
        runtime_virtualization_interface: VirtualizationInterface = None,
        runtime_database_interface: DatabaseInterface = None,
        runtime_port_forwarding_interface: PortForwardingInterface = None,
        enable_ssl: bool = DEFAULT_ENABLE_SSL,
        ssl_pem_private_key_file_path: str = None,
        ssl_pem_certificate_file_path: str = None,
    ):
        super().__init__(
            runtime_container_iso_file_path=runtime_container_iso_file_path,
            bind_address=None,
            listen_port=listen_port,
            client_timeout=None,
            runtime_virtualization_interface=runtime_virtualization_interface,
            runtime_database_interface=runtime_database_interface,
            runtime_port_forwarding_interface=runtime_port_forwarding_interface,
            runtime_rsa_wrapper=None,
            passive_mode=True,
        )

        self.listen_port = listen_port

        self.enable_ssl = enable_ssl
        self.ssl_pem_private_key_file_path = ssl_pem_private_key_file_path
        self.ssl_pem_certificate_file_path = ssl_pem_certificate_file_path

        self.request_handler_dict = {
            "": self._handle_home_from_http,  # If no verb is specified, return home data
            REQUEST_VERB_CREATE: self._handle_create_request_from_http,
            REQUEST_VERB_STAT: self._handle_stat_request_from_http,
            REQUEST_VERB_DESTROY: self._handle_destroy_request_from_http,
        }

    def _extract_post_request_args_values(self, request_args):
        container_uuid = (
            request_args.get(b"container_uuid")[0]
            if request_args.get(b"container_uuid")
            else None
        )
        client_token = (
            request_args.get(b"client_token")[0]
            if request_args.get(b"client_token")
            else None
        )

        return (
            container_uuid.decode() if container_uuid else None,
            client_token.decode() if client_token else None,
        )

    def _handle_error(
        self,
        exception_object=None,
        event=EVENT_RUNTIME_ERROR,
        message=RESPONSE_MSG_INTERNAL_ERROR,
        data={},
    ):
        traceback = (
            self._format_traceback(exception_object) if exception_object else None
        )
        result = self._execute_event_handler(
            event,
            CONTEXT_ERROR,
            data={
                "exception_object": exception_object,
                "traceback": traceback,
                "message": message,
            }
            | data,
        )

        if not result:
            result = makeResponse(False, message)[1]

        return result

    def _handle_home_from_http(self, request):
        return makeResponse(
            True,
            "Hello and welcome to this Anweddol server HTTP REST API. This server provides temporary, SSH-controllable virtual machines to enhance anonymity online.",
            data={
                "links": [
                    "https://the-anweddol-project.github.io/",
                    "https://github.com/the-anweddol-project/",
                    "https://anweddol-server.readthedocs.io/",
                ]
            },
        )[1]

    def _handle_stat_request_from_http(self, request):
        try:
            return self._handle_stat_request(
                passive_execution=True, request_object=request
            )

        except Exception as E:
            return self._handle_error(E, data={"request_object": request})

    def _handle_create_request_from_http(self, request):
        # Errors are already handled inside _handle_create_request
        return self._handle_create_request(
            passive_execution=True, request_object=request
        )

    def _handle_destroy_request_from_http(self, request):
        try:
            container_uuid, client_token = self._extract_post_request_args_values(
                request.args
            )

            if not container_uuid or not client_token:
                return self._handle_error(
                    event=EVENT_MALFORMED_REQUEST,
                    message=RESPONSE_MSG_BAD_REQ,
                    data={"request_object": request},
                )

            # Authentication related errors are handled inside _handle_destroy_request
            return self._handle_destroy_request(
                passive_execution=True,
                credentials_dict={
                    "container_uuid": container_uuid,
                    "client_token": client_token,
                },
                request_object=request,
            )

        except Exception as E:
            return self._handle_error(E, data={"request_object": request})

    def _handle_http_request(self, request):
        verb = None

        try:
            # Without this condition, URLs like http://<host>@<port>/foo/bar/stat
            # would be allowed on the server.
            if len(request.postpath) > 1:
                return self._handle_error(
                    event=EVENT_MALFORMED_REQUEST,
                    message=RESPONSE_MSG_BAD_REQ,
                    data={"request_object": request},
                )

            # Extract and transform the request verb into upper case
            verb = request.postpath[-1].decode().upper()

            http_method = request.method.decode()
            request_dict = {
                "verb": verb,
                "parameters": self._extract_post_request_args_values(request.args)
                if http_method == "POST"
                else {},
            }

            is_request_valid, request_content, request_errors = verifyRequestContent(
                request_dict
            )

            # If no verb is specified, it counts as valid request since
            # no verb means returning home data (see request_handler_dict comment)
            if not is_request_valid and verb != "":
                return self._handle_error(
                    event=EVENT_MALFORMED_REQUEST,
                    message=RESPONSE_MSG_BAD_REQ,
                    data={"request_object": request, "request_dict": request_dict},
                )

            result = self._execute_event_handler(
                EVENT_REQUEST,
                CONTEXT_NORMAL_PROCESS,
                data={"request_object": request, "request_dict": request_dict},
            )

            if result:
                return result

            if not self.request_handler_dict.get(verb):
                return self._handle_error(
                    event=EVENT_UNHANDLED_VERB,
                    message=RESPONSE_MSG_BAD_REQ,
                    data={"request_object": request, "request_dict": request_dict},
                )

            return self.request_handler_dict[verb](request=request)

        except Exception as E:
            return self._handle_error(
                E, data={"request_object": request, "request_dict": request_dict}
            )

    def _create_deferred_http_request_handle(self, request):
        def end(result, request):
            try:
                request.write(json.dumps(result).encode("utf8"))
                request.finish()

            except Exception as E:
                container_uuid = result["data"].get("container_uuid")

                if container_uuid:
                    container_instance = (
                        self.virtualization_interface.getStoredContainer(container_uuid)
                    )

                    if container_instance.isDomainRunning():
                        container_instance.stopDomain()

                        if (
                            self._execute_event_handler(
                                EVENT_CONTAINER_DOMAIN_STOPPED,
                                CONTEXT_ERROR,
                                data={
                                    "verb": REQUEST_VERB_CREATE,
                                    "request_object": request,
                                    "container_instance": container_instance,
                                },
                            )
                            == -1
                        ):
                            return

                    self._delete_container(container_instance)

                self._handle_error(
                    E, data={"verb": REQUEST_VERB_CREATE, "request_object": request}
                )

        def err(failure):
            return self._handle_error(
                data={"failure": failure, "request_object": request}
            )
            # return failure

        request.setHeader(b"content-type", b"application/json")

        d = threads.deferToThread(self._handle_http_request, request)
        d.addCallback(end, request)
        d.addErrback(err)

        return server.NOT_DONE_YET

    def _start_server(self):
        def process(reactor, *args):
            try:
                # reactor.addSystemEventTrigger("before", "shutdown", self._stop_server)

                if self.enable_ssl:
                    reactor.listenSSL(
                        self.listen_port,
                        server.Site(self),
                        ssl.DefaultOpenSSLContextFactory(
                            os.path.abspath(self.ssl_pem_private_key_file_path),
                            os.path.abspath(self.ssl_pem_certificate_file_path),
                        ),
                    )

                else:
                    endpoint = endpoints.TCP4ServerEndpoint(reactor, self.listen_port)
                    endpoint.listen(server.Site(self))

                self.start_timestamp = int(time.time())
                self.is_running = True

                threading.Thread(
                    target=self._delete_container_on_domain_shutdown_routine
                ).start()

                self._execute_event_handler(
                    EVENT_SERVER_STARTED, CONTEXT_NORMAL_PROCESS
                )

            except Exception as E:
                raise E

            return defer.Deferred()

        task.react(process)

    def _stop_server(self, die_on_error=False):
        try:
            self._delete_all_containers()
            self.database_interface.closeDatabase()

            self.is_running = False

            # reactor.running is set to True during startup to during shutdown,
            # which can lead to ReactorNotRunning raised if not timed properly.
            if reactor.running:
                try:
                    reactor.stop()

                except ReactorNotRunning:
                    pass

            self._execute_event_handler(EVENT_SERVER_STOPPED, CONTEXT_NORMAL_PROCESS)

        except Exception as E:
            if die_on_error:
                exit(0xDEAD)

            raise E

    def render_POST(self, request):
        return self._create_deferred_http_request_handle(request)

    def render_GET(self, request):
        return self._create_deferred_http_request_handle(request)

    def executeRequestHandler(
        self,
        verb: str,
        request: Request = None,
    ) -> None:
        if not self.request_handler_dict.get(verb):
            raise RuntimeError(f"The verb '{verb}' is not handled")

        return self.request_handler_dict[verb](request=request)
