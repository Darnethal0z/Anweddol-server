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
import shutil
import time
import json
import pwd
import sys
import os

# Intern importation
from .core.crypto import RSAWrapper, DEFAULT_RSA_KEY_SIZE
from .core.utilities import isPortBindable
from .tools.access_token import AccessTokenManager

from .utilities import createFileRecursively, checkServerEnvironment, Colors
from .config import loadConfigurationFileContent
from .process import launchServerProcess
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
  restart     restart the server

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
                shutil.copy(
                    f"{os.path.dirname(__file__)}/resources/config.yaml",
                    CONFIG_FILE_PATH,
                )

            self.config_content = loadConfigurationFileContent(CONFIG_FILE_PATH)

            if not self.config_content[0]:
                raise ValueError(
                    f"Configuration file is invalid : \n{json.dumps(self.config_content[1], indent=4)}"
                )
                exit(-1)

            self.config_content = self.config_content[1]

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

    def _log(self, message, bypass=False, color=None, end="\n", error=False):
        if not bypass:
            print(
                f"{color}{message}\033[0;0m" if color else message,
                end=end,
                file=sys.stderr if error else sys.stdout,
            )

    def _log_json(self, status, message, data={}, error=False):
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
            "--classic",
            help="run the classic server (the default option)",
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
            help="display logs in stdout",
            action="store_true",
        )
        parser.add_argument(
            "--enable-traceback-log",
            help="enable full tracebacks display in logs (for debug)",
            action="store_true",
        )
        parser.add_argument(
            "--skip-check", help="skip environment validity check", action="store_true"
        )
        parser.add_argument(
            "--json", help="print output in JSON format", action="store_true"
        )
        args = parser.parse_args(sys.argv[2:])

        self.json = args.json

        if not args.skip_check:
            check_result_list = checkServerEnvironment(self.config_content)

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
                        self._log(f"- {error}")

                    self._log("")

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

                    return -1

                else:
                    self._log(
                        "Server environment is invalid : ", color=Colors.RED, error=True
                    )

                    for error in check_result_list:
                        self._log(f"- {error}", error=True)

                    self._log("", error=True)

                    raise EnvironmentError(
                        f"{len(check_result_list)} error(s) detected on server environment"
                    )

        pid_file_path = self.config_content["server"].get("pid_file_path")

        if os.path.exists(pid_file_path):
            self._log(
                f"A PID file already exists on {pid_file_path}",
                bypass=args.json,
                color=Colors.YELLOW,
            )
            choice = (
                input("Kill the affiliated processus (y/n) ? : ")
                if not args.assume_yes and not args.assume_no
                else ("y" if args.assume_yes else "n")
            )

            if choice == "y":
                with open(pid_file_path, "r") as fd:
                    os.kill(int(fd.read()), signal.SIGTERM)

                while 1:
                    if isPortBindable(self.config_content["server"].get("listen_port")):
                        break

                    time.sleep(1)

            self._log("", bypass=args.json)

        if args.d:
            if args.json:
                if args.enable_stdout_log:
                    self._log_json(
                        LOG_JSON_STATUS_SUCCESS,
                        "Direct execution mode enabled, use CTRL+C to stop the server.",
                    )

            else:
                if args.enable_stdout_log:
                    self._log(
                        "Direct execution mode enabled, use CTRL+C to stop the server.\n",
                    )

            launchServerProcess(
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
                self._log("Server is starting")

            # https://pypi.org/project/python-daemon/
            with daemon.DaemonContext(
                uid=pwd.getpwnam(self.config_content["server"].get("user")).pw_uid,
                gid=pwd.getpwnam(self.config_content["server"].get("user")).pw_gid,
                pidfile=daemon.pidfile.PIDLockFile(pid_file_path),
            ):
                launchServerProcess(self.config_content)

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
        pid_file_path = self.config_content["server"].get("pid_file_path")

        if not os.path.exists(pid_file_path):
            if args.json:
                self._log_json(LOG_JSON_STATUS_SUCCESS, "Server is already stopped")

            else:
                self._log("Server is already stopped", color=Colors.RED)

            return 0

        with open(pid_file_path, "r") as fd:
            os.kill(int(fd.read()), signal.SIGTERM)

        if args.json:
            self._log_json(LOG_JSON_STATUS_SUCCESS, "Server is stopped")

        return 0

    def restart(self):
        parser = argparse.ArgumentParser(
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description="| Restart the server",
            usage=f"{sys.argv[0]} restart [OPT]",
        )
        parser.add_argument(
            "--json", help="print output in JSON format", action="store_true"
        )
        args = parser.parse_args(sys.argv[2:])

        self.json = args.json
        pid_file_path = self.config_content["server"].get("pid_file_path")

        if not os.path.exists(pid_file_path):
            if args.json:
                self._log_json(LOG_JSON_STATUS_SUCCESS, "Server is already stopped")

            else:
                self._log("Server is already stopped")

            return 0

        with open(pid_file_path, "r") as fd:
            os.kill(int(fd.read()), signal.SIGTERM)

            while 1:
                if isPortBindable(self.config_content["server"].get("listen_port")):
                    break

                time.sleep(1)

        if args.json:
            self._log_json(LOG_JSON_STATUS_SUCCESS, "Server is started")

        with daemon.DaemonContext(
            uid=pwd.getpwnam(self.config_content["server"].get("user")).pw_uid,
            gid=pwd.getpwnam(self.config_content["server"].get("user")).pw_gid,
            pidfile=daemon.pidfile.PIDLockFile(pid_file_path),
        ):
            launchServerProcess(self.config_content)

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
            "-r",
            help="delete a token",
            dest="delete_entry",
            metavar="ENTRY_ID",
            type=int,
        )
        parser.add_argument(
            "-e",
            help="enable a token",
            dest="enable_entry",
            metavar="ENTRY_ID",
            type=int,
        )
        parser.add_argument(
            "-d",
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
            new_entry_tuple = access_token_manager.addEntry(
                disable=True if args.disabled else False
            )

            if args.json:
                self._log_json(
                    LOG_JSON_STATUS_SUCCESS,
                    "New access token created",
                    data={
                        "entry_id": new_entry_tuple[0],
                        "access_token": new_entry_tuple[2],
                    },
                )

            else:
                self._log("New access token created", color=Colors.GREEN)
                self._log(f"Entry ID : {new_entry_tuple[0]}")
                self._log(f"Token : {new_entry_tuple[2]}")

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
                    self._log(f"== Entry ID {entry_id} ==")
                    self._log(
                        f"  Created : {datetime.fromtimestamp(creation_timestamp)}"
                    )
                    self._log(f"  Enabled : {bool(enabled)}\n")

        else:
            if args.delete_entry:
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

                    return 0

                access_token_manager.enableEntry(args.enable_entry)

                if args.json:
                    self._log_json(LOG_JSON_STATUS_SUCCESS, "Entry ID was enabled")
                    return 0

            else:
                if args.disable_entry:
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

                        return 0

                    access_token_manager.disableEntry(args.disable_entry)

                    if args.json:
                        self._log_json(LOG_JSON_STATUS_SUCCESS, "Entry ID was disabled")
                        return 0

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
                f"Fingerprint : {hashlib.sha256(new_rsa_wrapper.getPublicKey()).hexdigest()}"
            )

        return 0
