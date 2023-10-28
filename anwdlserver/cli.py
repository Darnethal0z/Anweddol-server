"""
Copyright 2023 The Anweddol project
See the LICENSE file for licensing informations
---

This module contains the 'anwdlserver' executable CLI process.

"""

from datetime import datetime
import daemon.pidfile
import argparse
import hashlib
import daemon
import signal
import time
import json
import pwd
import sys
import os

# Intern importation
from .core.crypto import RSAWrapper, DEFAULT_RSA_KEY_SIZE
from .core.utilities import isPortBindable, isInterfaceExists, isUserExists
from .tools.access_token import AccessTokenManager

from .utilities import createFileRecursively, Colors
from .config import loadConfigurationFileContent
from .process import launchServerProcess, SERVER_TYPE_CLASSIC, SERVER_TYPE_WEB
from .__init__ import __version__

# Constants definition
CONFIG_FILE_PATH = "/etc/anweddol/config.yaml"

LOG_JSON_STATUS_SUCCESS = "OK"
LOG_JSON_STATUS_ERROR = "ERROR"


class MainAnweddolServerCLI:
    def __init__(self):
        self.json = False

        parser = argparse.ArgumentParser(
            formatter_class=argparse.RawDescriptionHelpFormatter,
            usage=f"""{sys.argv[0]} <command> [OPT]

| The Anweddol server CLI implementation
| 
| Version {__version__}

server lifecycle commands:
  start       start the server
  stop        stop the server

server management commands:
  access-tk   manage access tokens
  regen-rsa   regenerate RSA keys""",
            epilog="""---
If you encounter any problems while using this tool,
please report it by opening an issue on the repository : 
 -> https://github.com/the-anweddol-project/Anweddol-server/issues""",
        )
        parser.add_argument("command", help="command to execute (see above)")
        args = parser.parse_args(sys.argv[1:2])

        if not hasattr(self, args.command.replace("-", "_")):
            parser.print_help()
            exit(-1)

        try:
            if not os.path.exists(CONFIG_FILE_PATH):
                raise FileNotFoundError(
                    f"The configuration file {CONFIG_FILE_PATH} was not found"
                )

            is_config_content_valid, config_document = loadConfigurationFileContent(
                CONFIG_FILE_PATH
            )
            if not is_config_content_valid:
                raise ValueError(
                    f"Configuration file is invalid : \n{json.dumps(config_document, indent=4)}"
                )
                exit(-1)

            self.config_content = config_document

            exit(getattr(self, args.command.replace("-", "_"))())

        except Exception as E:
            if type(E) is KeyboardInterrupt:
                self._log("")
                exit(0)

            if self.json:
                self._log_json(
                    LOG_JSON_STATUS_ERROR,
                    "An error occured",
                    data={"error": str(E)},
                    error=True,
                )

            else:
                self._log("An error occured : ", color=Colors.RED, end="", error=True)
                self._log(f"Error : {E}\n", error=True)

            exit(-1)

    def _check_server_environment(
        self, server_type=SERVER_TYPE_CLASSIC, server_config_key_name="server"
    ):
        container_iso_file_path = self.config_content["container"].get(
            "container_iso_file_path"
        )
        nat_interface_name = self.config_content["container"].get("nat_interface_name")
        listen_port = self.config_content[server_config_key_name].get("listen_port")
        user = self.config_content[server_config_key_name].get("user")
        errors_list = []

        if not isPortBindable(listen_port):
            errors_list.append(f"Port {listen_port} is not bindable")

        if not isInterfaceExists(nat_interface_name):
            errors_list.append(
                f"Interface '{nat_interface_name}' does not exists on system"
            )

        if not isUserExists(user):
            errors_list.append(f"User '{user}' does not exists on system")

        if not os.path.exists(container_iso_file_path):
            errors_list.append(f"{container_iso_file_path} was not found on system")

        if server_type == SERVER_TYPE_WEB and self.config_content["web_server"].get(
            "enable_ssl"
        ):
            for path in [
                self.config_content["web_server"].get("ssl_pem_private_key_file_path"),
                self.config_content["web_server"].get("ssl_pem_certificate_file_path"),
            ]:
                if not os.path.exists(path):
                    errors_list.append(f"{path} was not found on system")

        return errors_list

    def _log(self, message, bypass=False, color=None, end="\n", error=False):
        if bypass:
            return

        print(
            f"{color}{message}\033[0;0m" if color else message,
            end=end,
            file=sys.stderr if error else sys.stdout,
        )

    def _log_json(self, status, message, bypass=False, data={}, error=False):
        print(
            json.dumps({"status": status, "message": message, "data": data}),
            file=sys.stderr if error else sys.stdout,
        )

    def start(self):
        parser = argparse.ArgumentParser(
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description="| Start the server",
            usage=f"{sys.argv[0]} start [OPT]",
        )
        parser.add_argument(
            "-c",
            help="check environment validity",
            action="store_true",
        )
        parser.add_argument(
            "-d",
            help="execute the server in the parent terminal (will run as the actual effective user)",
            action="store_true",
        )
        parser.add_argument(
            "--web", help="run the web version of the server", action="store_true"
        )
        parser.add_argument(
            "--assume-yes", help="answer 'y' to any prompts", action="store_true"
        )
        parser.add_argument(
            "--assume-no", help="answer 'n' to any prompts", action="store_true"
        )
        parser.add_argument(
            "--enable-stdout-log",
            help="display logs in stdout during server run time",
            action="store_true",
        )
        parser.add_argument(
            "--enable-traceback-log",
            help="display full tracebacks display in logs during server run time (for debug)",
            action="store_true",
        )
        parser.add_argument(
            "--skip-check",
            help="skip server environment validity check",
            action="store_true",
        )
        parser.add_argument(
            "--json", help="print output in JSON format", action="store_true"
        )
        args = parser.parse_args(sys.argv[2:])

        self.json = args.json

        start_timestamp = 0
        elapsed_time = 0
        server_type = SERVER_TYPE_CLASSIC if not args.web else SERVER_TYPE_WEB
        server_config_key_name = (
            "server" if server_type == SERVER_TYPE_CLASSIC else "web_server"
        )
        server_user = self.config_content[server_config_key_name].get("user")
        server_pid_file_path = self.config_content[server_config_key_name].get(
            "pid_file_path"
        )

        if not args.skip_check:
            check_result_list = self._check_server_environment(
                server_type=server_type, server_config_key_name=server_config_key_name
            )

            if args.c:
                if args.json:
                    self._log_json(
                        LOG_JSON_STATUS_SUCCESS,
                        "Check done",
                        data={
                            "errors_recorded": len(check_result_list),
                            "errors_list": check_result_list,
                        },
                    )

                else:
                    self._log("Check done, ", end="")
                    self._log(
                        f"{len(check_result_list)} errors recorded{' :' if len(check_result_list) else ''}",
                        color=Colors.YELLOW if len(check_result_list) else Colors.GREEN,
                    )

                    for error in check_result_list:
                        self._log(f"  - {error}")

                return 0

            if len(check_result_list) != 0:
                if args.json:
                    self._log_json(
                        LOG_JSON_STATUS_ERROR,
                        "Errors detected on server environment",
                        data={
                            "errors_recorded": len(check_result_list),
                            "errors_list": check_result_list,
                        },
                        error=True,
                    )

                else:
                    self._log(
                        "Server environment is invalid : ", color=Colors.RED, error=True
                    )

                    for error in check_result_list:
                        self._log(f"  - {error}", error=True)

                return -1

                # raise EnvironmentError(
                #     f"{len(check_result_list)} error(s) detected on server environment"
                # )

        if os.path.exists(server_pid_file_path):
            self._log(
                f"The PID file {server_pid_file_path} already exists",
                bypass=args.json,
                color=Colors.YELLOW,
            )
            choice = (
                input("Kill the affiliated processus (y/n) ? : ")
                if not args.assume_yes and not args.assume_no
                else ("y" if args.assume_yes else "n")
            )

            if choice == "y":
                with open(server_pid_file_path, "r") as fd:
                    try:
                        os.kill(int(fd.read()), signal.SIGTERM)

                    except ProcessLookupError:
                        pass

                # Check if the previous server process is correctly stopped by
                # checking the availability of the listen port.
                while 1:
                    if isPortBindable(
                        self.config_content[server_config_key_name].get("listen_port")
                    ):
                        break

                    time.sleep(1)

        if args.d:
            if args.json:
                self._log_json(
                    LOG_JSON_STATUS_SUCCESS,
                    "Server is starting (direct mode enabled)",
                )

            else:
                self._log("Starting server (direct mode enabled) ...")

            start_timestamp = int(time.time())

            launchServerProcess(
                server_type,
                self.config_content,
                enable_stdout_log=args.enable_stdout_log,
                enable_traceback_on_log=args.enable_traceback_log,
            )

        else:
            if args.json:
                self._log_json(
                    LOG_JSON_STATUS_SUCCESS,
                    "Server is starting",
                )

            else:
                self._log("Starting server ...")

            start_timestamp = int(time.time())

            # https://pypi.org/project/python-daemon/
            with daemon.DaemonContext(
                uid=pwd.getpwnam(server_user).pw_uid,
                gid=pwd.getpwnam(server_user).pw_gid,
                pidfile=daemon.pidfile.PIDLockFile(server_pid_file_path),
            ):
                launchServerProcess(server_type, self.config_content)

        elapsed_time = int(time.time()) - start_timestamp

        if args.json:
            self._log_json(
                LOG_JSON_STATUS_SUCCESS,
                "Server process ended",
                data={"elapsed_time": elapsed_time},
            )

        else:
            self._log("Server process ended", color=Colors.GREEN)
            self._log(f"  Elapsed time : {elapsed_time} seconds")

        return 0

    def stop(self):
        parser = argparse.ArgumentParser(
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description="""| Stop the server""",
            usage=f"{sys.argv[0]} stop [OPT]",
        )
        parser.add_argument(
            "--json", help="print output in JSON format", action="store_true"
        )
        args = parser.parse_args(sys.argv[2:])

        self.json = args.json

        old_server_process_pid = None

        for pid_file_path in [
            self.config_content["server"].get("pid_file_path"),
            self.config_content["web_server"].get("pid_file_path"),
        ]:
            if not os.path.exists(pid_file_path):
                continue

            with open(pid_file_path, "r") as fd:
                old_server_process_pid = int(fd.read())

            try:
                os.kill(old_server_process_pid, signal.SIGTERM)

            except ProcessLookupError:
                pass

            # Stop the loop at the first PID file found
            break

        if not old_server_process_pid:
            if args.json:
                self._log_json(
                    LOG_JSON_STATUS_ERROR, "No PID file were found", error=True
                )

            else:
                self._log("No PID file were found", error=True, color=Colors.RED)

            return -1

        if args.json:
            self._log_json(
                LOG_JSON_STATUS_SUCCESS,
                "Server was stopped",
                data={"old_server_process_pid": old_server_process_pid},
            )

        else:
            self._log(
                f"Process with PID {old_server_process_pid} was stopped",
                color=Colors.GREEN,
            )

        return 0

    def access_tk(self):
        parser = argparse.ArgumentParser(
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description="""| Manage access tokens""",
            usage=f"{sys.argv[0]} access-tk [OPT]",
        )
        parser.add_argument("-a", help="add a new token entry", action="store_true")
        parser.add_argument("-l", help="list token entries", action="store_true")
        parser.add_argument(
            "-d",
            help="delete a token",
            dest="delete_entry",
            metavar="ENTRY_ID",
            type=int,
        )
        parser.add_argument(
            "--enable",
            help="enable a token",
            dest="enable_entry",
            metavar="ENTRY_ID",
            type=int,
        )
        parser.add_argument(
            "--disable",
            help="disable a token",
            dest="disable_entry",
            metavar="ENTRY_ID",
            type=int,
        )
        parser.add_argument(
            "--disabled",
            help="disable the created access token by default",
            action="store_true",
        )
        parser.add_argument(
            "--json", help="print output in JSON format", action="store_true"
        )
        args = parser.parse_args(sys.argv[2:])

        self.json = args.json

        access_token_database_file_path = self.config_content["access_token"].get(
            "access_token_database_file_path"
        )

        if not os.path.exists(access_token_database_file_path):
            createFileRecursively(access_token_database_file_path)

        access_token_manager = AccessTokenManager(access_token_database_file_path)

        if args.a:
            entry_id, _, access_token = access_token_manager.addEntry(
                disable=True if args.disabled else False
            )

            if args.json:
                self._log_json(
                    LOG_JSON_STATUS_SUCCESS,
                    "New access token created",
                    data={
                        "entry_id": entry_id,
                        "access_token": access_token,
                    },
                )

            else:
                self._log("New access token created", color=Colors.GREEN)
                self._log(f"  Entry ID : {entry_id}")
                self._log(f"  Token : {access_token}")

        elif args.l:
            if args.json:
                entry_list = access_token_manager.listEntries()

                self._log_json(
                    LOG_JSON_STATUS_SUCCESS,
                    "Recorded entries ID",
                    data={"entry_list": entry_list},
                )

            else:
                for (
                    entry_id,
                    creation_timestamp,
                    enabled,
                ) in access_token_manager.listEntries():
                    self._log(f"- Entry ID {entry_id}")
                    self._log(
                        f"  Created : {datetime.fromtimestamp(creation_timestamp)}"
                    )
                    self._log(f"  Enabled : {bool(enabled)}\n")

        elif args.delete_entry:
            if not access_token_manager.getEntry(args.delete_entry):
                if args.json:
                    self._log_json(
                        LOG_JSON_STATUS_ERROR,
                        f"Entry ID {args.delete_entry} does not exists on database",
                        error=True,
                    )

                else:
                    self._log(
                        f"Entry ID {args.delete_entry} does not exists on database",
                        error=True,
                        color=Colors.RED,
                    )

            else:
                access_token_manager.deleteEntry(args.delete_entry)

                if args.json:
                    self._log_json(LOG_JSON_STATUS_SUCCESS, "Entry ID was deleted")

        elif args.enable_entry:
            if not access_token_manager.getEntry(args.enable_entry):
                if args.json:
                    self._log_json(
                        LOG_JSON_STATUS_ERROR,
                        f"Entry ID {args.enable_entry} does not exists on database",
                        error=True,
                    )

                else:
                    self._log(
                        f"Entry ID {args.enable_entry} does not exists on database",
                        error=True,
                        color=Colors.RED,
                    )

            else:
                access_token_manager.enableEntry(args.enable_entry)

                if args.json:
                    self._log_json(LOG_JSON_STATUS_SUCCESS, "Entry ID was enabled")

        elif args.disable_entry:
            if not access_token_manager.getEntry(args.disable_entry):
                if args.json:
                    self._log_json(
                        LOG_JSON_STATUS_ERROR,
                        f"Entry ID {args.disable_entry} does not exists on database",
                        error=True,
                    )

                else:
                    self._log(
                        f"Entry ID {args.disable_entry} does not exists on database",
                        error=True,
                        color=Colors.RED,
                    )

            else:
                access_token_manager.disableEntry(args.disable_entry)

                if args.json:
                    self._log_json(LOG_JSON_STATUS_SUCCESS, "Entry ID was disabled")

        access_token_manager.closeDatabase()

        return 0

    def regen_rsa(self):
        parser = argparse.ArgumentParser(
            description="| Regenerate RSA keys",
            usage=f"{sys.argv[0]} regen-rsa [OPT]",
        )
        parser.add_argument(
            "-b",
            help=f"specify the key size, in bytes (default is {DEFAULT_RSA_KEY_SIZE})",
            dest="key_size",
            type=int,
        )
        parser.add_argument(
            "--json", help="print output in JSON format", action="store_true"
        )
        args = parser.parse_args(sys.argv[2:])

        self.json = args.json

        new_rsa_wrapper = RSAWrapper(
            key_size=args.key_size if args.key_size else DEFAULT_RSA_KEY_SIZE
        )

        public_key_path = self.config_content["server"].get("public_rsa_key_file_path")
        private_key_path = self.config_content["server"].get(
            "private_rsa_key_file_path"
        )

        if not os.path.exists(public_key_path):
            createFileRecursively(public_key_path)

        if not os.path.exists(private_key_path):
            createFileRecursively(private_key_path)

        with open(public_key_path, "w") as fd:
            fd.write(new_rsa_wrapper.getPublicKey().decode())

        with open(private_key_path, "w") as fd:
            fd.write(new_rsa_wrapper.getPrivateKey().decode())

        if args.json:
            self._log_json(
                LOG_JSON_STATUS_SUCCESS,
                "RSA keys re-generated",
                data={
                    "fingerprint": hashlib.sha256(
                        new_rsa_wrapper.getPublicKey()
                    ).hexdigest()
                },
            )

        else:
            self._log("RSA keys re-generated", color=Colors.GREEN)
            self._log(
                f"  Fingerprint : {hashlib.sha256(new_rsa_wrapper.getPublicKey()).hexdigest()}"
            )

        return 0
