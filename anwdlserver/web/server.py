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
from twisted.internet import reactor, task, defer, ssl, endpoints
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
from ..core.sanitization import makeResponse

DEFAULT_RESTWEBSERVER_LISTEN_PORT = 8080
DEFAULT_ENABLE_SSL = False


class RESTWebServerInterface(ServerInterface, resource.Resource):
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

        # request_handler_dict redefinition from ServerInterface
        self.request_handler_dict = {
            "": self._handle_http_home,  # If no verb is specified, return home data
            REQUEST_VERB_CREATE: self._handle_http_create_request,
            REQUEST_VERB_STAT: self._handle_http_stat_request,
            REQUEST_VERB_DESTROY: self._handle_http_destroy_request,
        }

    def _remove_dict_key(self, dict_, key):
        new_dict = dict_
        del new_dict[key]

        return new_dict

    def _extract_post_request_args_values(self, request_args):
        container_uuid = request_args.get(b"container_uuid")
        client_token = request_args.get(b"client_token")

        return (
            container_uuid[0].decode() if container_uuid else None,
            client_token[0].decode() if client_token else None,
        )

    def _handle_error(
        self,
        error=None,
        event=EVENT_RUNTIME_ERROR,
        message=RESPONSE_MSG_INTERNAL_ERROR,
        data={},
    ):
        result_data = {"traceback": error} if error else {}
        result_data.update(data)

        result = self._execute_event_handler(event, CONTEXT_ERROR, data=result_data)

        if not result:
            result = makeResponse(False, message)[1]

        return result

    def _handle_http_home(self, request):
        return makeResponse(
            True,
            "Hello and welcome to this Anweddol server REST API. This server provides temporary, SSH-controllable virtual machines to enhance anonymity online.",
            data={
                "links": [
                    "https://the-anweddol-project.github.io/",
                    "https://github.com/the-anweddol-project/",
                    "https://anweddol-server.readthedocs.io/",
                ]
            },
        )[1]

    def _handle_http_stat_request(self, request):
        try:
            return self._handle_stat_request(passive_execution=True)

        except Exception as E:
            return self._handle_error(
                self._format_traceback(E), data={"request": request}
            )

    def _handle_http_create_request(self, request):
        # Errors are already handled inside _handle_create_request
        return self._handle_create_request(passive_execution=True)

    def _handle_http_destroy_request(self, request):
        try:
            container_uuid, client_token = self._extract_post_request_args_values(
                request.args
            )

            if not container_uuid or not client_token:
                return self._handle_error(
                    event=EVENT_MALFORMED_REQUEST, message=RESPONSE_MSG_BAD_REQ
                )

            # Authentication errors are already handled inside _handle_destroy_request
            return self._handle_destroy_request(
                passive_execution=True,
                credentials_dict={
                    "container_uuid": container_uuid,
                    "client_token": client_token,
                },
            )

        except Exception as E:
            return self._handle_error(
                self._format_traceback(E), data={"request": request}
            )

    def _handle_http_request(self, request):
        try:
            # Extract and transform the verb into upper case
            verb = request.postpath[-1].decode().upper()

            result = self._execute_event_handler(
                EVENT_REQUEST,
                CONTEXT_NORMAL_PROCESS,
                data={"verb": verb, "request": request},
            )

            if result:
                return result

            # Without this condition, URLs like http://<host>@<port>/foo/bar/stat
            # would be allowed on the server.
            if len(request.postpath) > 1:
                return self._handle_error(
                    event=EVENT_MALFORMED_REQUEST, message=RESPONSE_MSG_BAD_REQ
                )

            if not self.request_handler_dict.get(verb):
                return self._handle_error(
                    event=EVENT_UNHANDLED_VERB, message=RESPONSE_MSG_BAD_REQ
                )

            return self.request_handler_dict[verb](request)

        except Exception as E:
            return self._handle_error(self._format_traceback(E))

    def _start_server(self):
        def process(reactor, *args):
            try:
                reactor.addSystemEventTrigger("before", "shutdown", self._stop_server)

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
                self._handle_error(self._format_traceback(E))

            return defer.Deferred()

        task.react(process)

    def _stop_server(self, raise_errors=False, die_on_error=False):
        try:
            self._delete_all_containers()
            self.database_interface.closeDatabase()

            self.is_running = False

            if reactor.running:
                # reactor.running is set to True during startup to during shutdown,
                # which can lead to ReactorNotRunning raised if not timed properly.
                try:
                    reactor.stop()
                except ReactorNotRunning:
                    pass

            self._execute_event_handler(EVENT_SERVER_STOPPED, CONTEXT_NORMAL_PROCESS)

        except Exception as E:
            if raise_errors:
                raise E

            self._handle_error(self._format_traceback(E))

            if die_on_error:
                exit(0xDEAD)

    def render_POST(self, request):
        request.setHeader(b"content-type", b"application/json")

        return json.dumps(self._handle_http_request(request)).encode("utf8")

    def render_GET(self, request):
        request.setHeader(b"content-type", b"application/json")

        return json.dumps(self._handle_http_request(request)).encode("utf8")

    def executeRequestHandler(
        self,
        verb: str,
        request: Request = None,
    ):
        if not self.request_handler_dict.get(verb):
            raise RuntimeError(f"The verb '{verb}' is not handled")

        return self.request_handler_dict[verb](request)
