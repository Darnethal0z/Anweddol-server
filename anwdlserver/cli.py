"""
    Copyright 2023 The Anweddol project
    See the LICENSE file for licensing informations
    ---

    CLI : Main anwdlserver CLI process

"""
from datetime import datetime
import daemon.pidfile
import argparse
import hashlib
import daemon
import signal
import json
import pwd
import sys
import os

# Intern importation
from .core.crypto import RSAWrapper, DEFAULT_RSA_KEY_SIZE
from .core.util import (
    isPortBindable,
    isInterfaceExists,
    isUserExists,
)
from .tools.accesstk import AccessTokenManager
from .config import ConfigurationFileManager
from .__init__ import __version__
from .process import (
    launchServerProcess,
    PUBLIC_PEM_KEY_FILENAME,
    PRIVATE_PEM_KEY_FILENAME,
)

# Constants definition
CONFIG_FILE_PATH = (
    "C:\\Windows\\Anweddol\\config.yaml"
    if os.name == "nt"
    else "/etc/anweddol/config.yaml"
)

LOG_START_ERROR = "x>"
LOG_START_INFO = "i>"
LOG_START_WARNING = "!>"
LOG_START_SUCCESS = "+>"

LOG_JSON_STATUS_SUCCESS = "OK"
LOG_JSON_STATUS_ERROR = "ERROR"


class MainAnweddolServerCLI:
    def __init__(self):
        self.json = False

        parser = argparse.ArgumentParser(
            formatter_class=argparse.RawDescriptionHelpFormatter,
            usage=f"""{sys.argv[0]} <command> [OPT]

\033[1mThe Anweddol server CLI implementation.\033[0m
Provide clients with containers and manage them.

Version {__version__}

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
                raise FileNotFoundError(f"{CONFIG_FILE_PATH} was not found on system")

            self.config_manager = ConfigurationFileManager(CONFIG_FILE_PATH)
            self.config_content = self.config_manager.loadContent()

            if not self.config_content[0]:
                raise ValueError(
                    f"Invalid configuration file :\n{json.dumps(self.config_content[1], indent=4)}"
                )

            self.config_content = self.config_content[1]

        except Exception as E:
            self.__log(
                LOG_START_ERROR, f"Error during configuration file processing : {E}"
            )
            exit(-1)

        try:
            getattr(self, args.command.replace("-", "_"))()
            exit(0)

        except Exception as E:
            if self.json:
                self.__log_json(
                    LOG_JSON_STATUS_ERROR, "An error occured", data={"error": str(E)}
                )

            else:
                self.__log(LOG_START_ERROR, f"Error : {E}")

            exit(-1)

    def __log(self, start=None, message="", tabulation=False, bypass=False):
        if bypass:
            return

        print(
            ("    " if tabulation else "")
            + (("\n" + start + " ") if start else "")
            + message
            + ("\n" if start else ""),
            file=sys.stderr
            if (start == LOG_START_ERROR or start == LOG_START_WARNING)
            else sys.stdout,
        )

    def __log_json(self, status, message, data={}):
        print(json.dumps({"status": status, "message": message, "data": data}))

    def __create_file_recursively(self, file_path, dir_folder_only=False):
        try:
            os.makedirs(os.path.dirname(file_path))

        except FileExistsError:
            pass

        if dir_folder_only:
            return

        with open(file_path, "w") as fd:
            fd.close()

    def start(self):
        parser = argparse.ArgumentParser(
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description="\033[1m-> Start the server\033[0m",
            usage=f"{sys.argv[0]} start [OPT]",
        )
        parser.add_argument(
            "-c",
            help="check environment validity",
            action="store_true",
        )
        parser.add_argument(
            "-d",
            help="execute the server in direct mode (parent terminal). Server will run as the actual effective user",
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

        if os.path.exists(self.config_content["paths"].get("pid_file_path")):
            raise RuntimeError("The server is already running")

        if not args.skip_check:
            self.__log(message="Verifying server environment ...", bypass=args.json)

            counter = 0
            errors_list = []

            if not isPortBindable(self.config_content["server"].get("listen_port")):
                self.__log(
                    message=f"\033[0;31mPort {self.config_content['server'].get('listen_port')} is not bindable\033[0m",
                    tabulation=True,
                    bypass=args.json,
                )

                counter += 1
                errors_list.append(
                    f"Port {self.config_content['server'].get('listen_port')} is not bindable"
                )

            if not isInterfaceExists(
                self.config_content["container"].get("nat_interface_name")
            ):
                self.__log(
                    message=f"\033[0;31mInterface '{self.config_content['container'].get('nat_interface_name')}' does not exists on system\033[0m",
                    tabulation=True,
                    bypass=args.json,
                )

                counter += 1
                errors_list.append(
                    f"Interface '{self.config_content['container'].get('nat_interface_name')}' does not exists on system"
                )

            if not isInterfaceExists(
                self.config_content["container"].get("bridge_interface_name")
            ):
                self.__log(
                    message=f"\033[0;31mInterface '{self.config_content['container'].get('bridge_interface_name')}' does not exists on system\033[0m",
                    tabulation=True,
                    bypass=args.json,
                )

                counter += 1
                errors_list.append(
                    f"Interface '{self.config_content['container'].get('bridge_interface_name')}' does not exists on system"
                )

            if not isUserExists(self.config_content["server"].get("user")):
                self.__log(
                    message=f"\033[0;31mUser '{self.config_content['server'].get('user')}' does not exists on system\033[0m",
                    tabulation=True,
                    bypass=args.json,
                )

                counter += 1
                errors_list.append(
                    f"User '{self.config_content['server'].get('user')}' does not exists on system"
                )

            if not os.path.exists(
                self.config_content["paths"].get("container_iso_path")
            ):
                self.__log(
                    message=f"\033[0;31m{self.config_content['paths'].get('container_iso_path')} was not found on system\033[0m",
                    tabulation=True,
                    bypass=args.json,
                )

                counter += 1
                errors_list.append(
                    f"{self.config_content['paths'].get('container_iso_path')} was not found on system"
                )

            if args.c:
                if args.json:
                    self.__log_json(
                        LOG_JSON_STATUS_SUCCESS,
                        "Check done",
                        data={"errors_recorded": counter, "errors_list": errors_list},
                    )

                else:
                    self.__log(
                        LOG_START_INFO,
                        f"Check done. {counter} error(s) recorded",
                    )

                return

            if counter != 0:
                if args.json:
                    self.__log_json(
                        LOG_JSON_STATUS_ERROR,
                        "Errors detected on server environment",
                        data={"errors_recorded": counter, "errors_list": errors_list},
                    )
                    return

                else:
                    raise EnvironmentError(
                        f"{counter} error(s) detected on server environment"
                    )

        self.__log(message="Starting server ...", bypass=args.json)

        if args.d:
            self.__log(
                message="INFO : Direct execution mode enabled. Use CTRL+C to stop the server.",
                bypass=args.json,
            )
            launchServerProcess(self.config_content)

        else:
            # https://pypi.org/project/python-daemon/
            with daemon.DaemonContext(
                uid=pwd.getpwnam(self.config_content["server"].get("user")).pw_uid,
                gid=pwd.getpwnam(self.config_content["server"].get("user")).pw_gid,
                pidfile=daemon.pidfile.PIDLockFile(
                    self.config_content["paths"].get("pid_file_path")
                ),
            ):
                launchServerProcess(self.config_content)

            if args.json:
                self.__log_json(LOG_JSON_STATUS_SUCCESS, "Server is started")
                return

            self.__log(
                LOG_START_SUCCESS,
                "Server is started",
            )

    def stop(self):
        parser = argparse.ArgumentParser(
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description="""\033[1m-> Stop the server\033[0m

Sends a SIGINT signal to the server daemon to stop it.""",
            usage=f"{sys.argv[0]} stop [OPT]",
        )
        parser.add_argument(
            "--json", help="print output in JSON format", action="store_true"
        )
        args = parser.parse_args(sys.argv[2:])

        self.json = args.json

        self.__log(message="Stopping server ...", bypass=args.json)

        if not os.path.exists(self.config_content["paths"].get("pid_file_path")):
            raise RuntimeError("The server is not running")

        with open(self.config_content["paths"].get("pid_file_path"), "r") as fd:
            os.kill(int(fd.read()), signal.SIGTERM)

        if args.json:
            self.__log_json(LOG_JSON_STATUS_SUCCESS, "Server is stopped")
            return

        self.__log(
            LOG_START_SUCCESS,
            "Server is stopped",
        )

    def restart(self):
        parser = argparse.ArgumentParser(
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description="\033[1m-> Restart the server\033[0m",
            usage=f"{sys.argv[0]} restart [OPT]",
        )
        parser.add_argument(
            "--json", help="print output in JSON format", action="store_true"
        )
        args = parser.parse_args(sys.argv[2:])

        self.json = args.json

        self.__log(
            message="Restarting server ...",
            bypass=args.json,
        )

        if not os.path.exists(self.config_content["paths"].get("pid_file_path")):
            raise RuntimeError("The server is not running")

        with open(self.config_content["paths"].get("pid_file_path"), "r") as fd:
            os.kill(int(fd.read()), signal.SIGTERM)

        with daemon.DaemonContext(
            uid=pwd.getpwnam(self.config_content["server"].get("user")).pw_uid,
            gid=pwd.getpwnam(self.config_content["server"].get("user")).pw_gid,
            pidfile=daemon.pidfile.PIDLockFile(
                self.config_content["paths"].get("pid_file_path")
            ),
        ):
            launchServerProcess(self.config_content)

        if args.json:
            self.__log_json(LOG_JSON_STATUS_SUCCESS, "Server is started")
            return

        self.__log(
            LOG_START_SUCCESS,
            "Server is started",
            bypass=args.json,
        )

    def access_tk(self):
        parser = argparse.ArgumentParser(
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description="""\033[1m-> Manage access tokens\033[0m""",
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

        if not os.path.exists(
            self.config_content["paths"].get("access_tokens_database_path")
        ):
            self.__create_file_recursively(
                self.config_content["paths"].get("access_tokens_database_path")
            )

        access_token_manager = AccessTokenManager(
            self.config_content["paths"].get("access_tokens_database_path")
        )

        if args.a:
            self.__log(
                message="Creating access token ...",
                bypass=args.json,
            )

            new_entry_tuple = access_token_manager.addEntry(
                disable=True if args.disabled else False
            )

            if args.json:
                self.__log_json(
                    LOG_JSON_STATUS_SUCCESS,
                    "New access token created",
                    data={
                        "entry_id": new_entry_tuple[0],
                        "access_token": new_entry_tuple[2],
                    },
                )

                return

            self.__log(
                LOG_START_SUCCESS,
                f"New access token created (Entry ID : {new_entry_tuple[0]})",
            )
            self.__log(
                message=f"Token : {new_entry_tuple[2]}\n",
                tabulation=True,
            )

        elif args.l:
            if args.json:
                entry_list = access_token_manager.listEntries()

                self.__log_json(
                    LOG_JSON_STATUS_SUCCESS,
                    "Recorded entries ID",
                    data={"entry_list": entry_list},
                )

                return

            self.__log(
                message="Listing recorded entries ID ...",
            )

            for entries in access_token_manager.listEntries():
                self.__log(
                    message=f"\n  - Entry ID {entries[0]}",
                )
                self.__log(
                    message=f"     Created : {datetime.fromtimestamp(entries[1])}",
                    tabulation=True,
                )
                self.__log(
                    message=f"     Enabled : {bool(entries[2])}",
                    tabulation=True,
                )

            self.__log(LOG_START_SUCCESS, "Done")

        else:

            def __check_entry_existence(entry_id):
                if not access_token_manager.getEntry(entry_id):
                    access_token_manager.closeDatabase()
                    raise LookupError(
                        f"Entry ID {entry_id} does not exists on database"
                    )

            if args.delete_entry:
                __check_entry_existence(args.delete_entry)
                access_token_manager.deleteEntry(args.delete_entry)

                if args.json:
                    self.__log_json(LOG_JSON_STATUS_SUCCESS, "Entry ID was deleted")
                    return

                self.__log(
                    LOG_START_SUCCESS,
                    f"Entry ID {args.delete_entry} was deleted",
                )

            elif args.enable_entry:
                __check_entry_existence(args.enable_entry)
                access_token_manager.enableEntry(args.enable_entry)

                if args.json:
                    self.__log_json(LOG_JSON_STATUS_SUCCESS, "Entry ID was enabled")
                    return

                self.__log(
                    LOG_START_SUCCESS,
                    f"Entry ID {args.enable_entry} was enabled",
                )

            else:
                if args.disable_entry:
                    __check_entry_existence(args.disable_entry)
                    access_token_manager.disableEntry(args.disable_entry)

                    if args.json:
                        self.__log_json(
                            LOG_JSON_STATUS_SUCCESS, "Entry ID was disabled"
                        )
                        return

                    self.__log(
                        LOG_START_SUCCESS,
                        f"Entry ID {args.disable_entry} was disabled",
                    )

        access_token_manager.closeDatabase()

    def regen_rsa(self):
        parser = argparse.ArgumentParser(
            description="\033[1m-> Regenerate RSA keys\033[0m",
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

        self.__log(
            message=f"Generating {args.key_size if args.key_size else DEFAULT_RSA_KEY_SIZE} bytes RSA key pair ...",
            bypass=args.json,
        )

        new_rsa_wrapper = RSAWrapper(
            key_size=args.key_size if args.key_size else DEFAULT_RSA_KEY_SIZE
        )

        if not os.path.exists(self.config_content["paths"].get("rsa_keys_root_path")):
            self.__create_file_recursively(
                self.config_content["paths"].get("rsa_keys_root_path"),
                dir_folder_only=True,
            )

        with open(
            self.config_content["paths"].get("rsa_keys_root_path")
            + "/"
            + PRIVATE_PEM_KEY_FILENAME,
            "w",
        ) as fd:
            fd.write(new_rsa_wrapper.getPrivateKey().decode())

        with open(
            self.config_content["paths"].get("rsa_keys_root_path")
            + "/"
            + PUBLIC_PEM_KEY_FILENAME,
            "w",
        ) as fd:
            fd.write(new_rsa_wrapper.getPublicKey().decode())

        new_fingerprint = hashlib.sha256(new_rsa_wrapper.getPublicKey()).hexdigest()

        if args.json:
            self.__log_json(
                LOG_JSON_STATUS_SUCCESS,
                "RSA keys re-generated",
                data={"fingerprint": new_fingerprint},
            )
            return

        self.__log(
            LOG_START_SUCCESS,
            "RSA keys re-generated",
        )
        self.__log(
            message=f"Fingerprint : {new_fingerprint}",
            tabulation=True,
        )
