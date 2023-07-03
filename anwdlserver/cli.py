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
import time
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

        except KeyboardInterrupt:
            self.__log_stdout("")
            exit(0)

        except Exception as E:
            self.__log_stdout(f"Error during configuration file processing : {E}\n")
            exit(-1)

        try:
            getattr(self, args.command.replace("-", "_"))()
            exit(0)

        except KeyboardInterrupt:
            self.__log_stdout("")
            exit(0)

        except Exception as E:
            if self.json:
                self.__log_json(
                    LOG_JSON_STATUS_ERROR, "An error occured", data={"error": str(E)}
                )

            else:
                self.__log_stdout(f"An error occured : {E}\n")

            exit(-1)

    def __log_stdout(self, message, bypass=False):
        if not bypass:
            print(message)

    def __log_json(self, status, message, data={}):
        print(json.dumps({"status": status, "message": message, "data": data}))

    def __create_file_recursively(self, path, is_folder=False):
        try:
            os.makedirs(os.path.dirname(path) if not is_folder else path)

        except FileExistsError:
            pass

        if is_folder:
            return

        with open(path, "w") as fd:
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
            "-y", "--assume-yes", help="answer 'y' to any prompts", action="store_true"
        )
        parser.add_argument(
            "-n", "--assume-no", help="answer 'n' to any prompts", action="store_true"
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
            self.__log_stdout(
                f"A PID file already exists on {self.config_content['paths'].get('pid_file_path')}",
                bypass=args.json,
            )
            choice = (
                input(" ↳ Kill the affiliated processus (y/n) ? : ")
                if not args.assume_yes and not args.assume_no
                else ("y" if args.assume_yes else "n")
            )

            if choice == "y":
                with open(self.config_content["paths"].get("pid_file_path"), "r") as fd:
                    os.kill(int(fd.read()), signal.SIGTERM)

                while 1:
                    if isPortBindable(self.config_content["server"].get("listen_port")):
                        break

                    time.sleep(1)

            self.__log_stdout("", bypass=args.json)

        if not args.skip_check:
            counter = 0
            errors_list = []

            if not isPortBindable(self.config_content["server"].get("listen_port")):
                self.__log_stdout(
                    f"- Port {self.config_content['server'].get('listen_port')} is not bindable",
                    bypass=args.json,
                )

                counter += 1
                errors_list.append(
                    f"Port {self.config_content['server'].get('listen_port')} is not bindable"
                )

            if not isInterfaceExists(
                self.config_content["container"].get("nat_interface_name")
            ):
                self.__log_stdout(
                    f"- Interface '{self.config_content['container'].get('nat_interface_name')}' does not exists on system",
                    bypass=args.json,
                )

                counter += 1
                errors_list.append(
                    f"Interface '{self.config_content['container'].get('nat_interface_name')}' does not exists on system"
                )

            if not isInterfaceExists(
                self.config_content["container"].get("bridge_interface_name")
            ):
                self.__log_stdout(
                    f"- Interface '{self.config_content['container'].get('bridge_interface_name')}' does not exists on system",
                    bypass=args.json,
                )

                counter += 1
                errors_list.append(
                    f"Interface '{self.config_content['container'].get('bridge_interface_name')}' does not exists on system"
                )

            if not isUserExists(self.config_content["server"].get("user")):
                self.__log_stdout(
                    f"- User '{self.config_content['server'].get('user')}' does not exists on system",
                    bypass=args.json,
                )

                counter += 1
                errors_list.append(
                    f"User '{self.config_content['server'].get('user')}' does not exists on system"
                )

            if not os.path.exists(
                self.config_content["paths"].get("container_iso_path")
            ):
                self.__log_stdout(
                    f"- {self.config_content['paths'].get('container_iso_path')} was not found on system",
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
                    self.__log_stdout(
                        f"\nCheck done. {counter} error(s) recorded\n", bypass=args.json
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

        if args.d:
            self.__log_stdout(
                "Direct execution mode enabled. Use CTRL+C to stop the server.",
                bypass=args.json,
            )
            launchServerProcess(self.config_content)

        else:
            if args.json:
                self.__log_json(
                    LOG_JSON_STATUS_SUCCESS,
                    "Server is started",
                )

            # https://pypi.org/project/python-daemon/
            with daemon.DaemonContext(
                uid=pwd.getpwnam(self.config_content["server"].get("user")).pw_uid,
                gid=pwd.getpwnam(self.config_content["server"].get("user")).pw_gid,
                pidfile=daemon.pidfile.PIDLockFile(
                    self.config_content["paths"].get("pid_file_path")
                ),
            ):
                launchServerProcess(self.config_content)

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

        if not os.path.exists(self.config_content["paths"].get("pid_file_path")):
            if args.json:
                self.__log_json(LOG_JSON_STATUS_SUCCESS, "Server is already stopped")
                return

            self.__log_stdout("Server is already stopped\n")
            return

        with open(self.config_content["paths"].get("pid_file_path"), "r") as fd:
            os.kill(int(fd.read()), signal.SIGTERM)

        if args.json:
            self.__log_json(LOG_JSON_STATUS_SUCCESS, "Server is stopped")
            return

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

        if not os.path.exists(self.config_content["paths"].get("pid_file_path")):
            if args.json:
                self.__log_json(LOG_JSON_STATUS_SUCCESS, "Server is already stopped")
                return

            self.__log_stdout("Server is already stopped\n")
            return

        with open(self.config_content["paths"].get("pid_file_path"), "r") as fd:
            os.kill(int(fd.read()), signal.SIGTERM)

            while 1:
                if isPortBindable(self.config_content["server"].get("listen_port")):
                    break

                time.sleep(1)

        if args.json:
            self.__log_json(LOG_JSON_STATUS_SUCCESS, "Server is started")
            return

        with daemon.DaemonContext(
            uid=pwd.getpwnam(self.config_content["server"].get("user")).pw_uid,
            gid=pwd.getpwnam(self.config_content["server"].get("user")).pw_gid,
            pidfile=daemon.pidfile.PIDLockFile(
                self.config_content["paths"].get("pid_file_path")
            ),
        ):
            launchServerProcess(self.config_content)

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

            self.__log_stdout(
                f"New access token created (Entry ID : {new_entry_tuple[0]})"
            )
            self.__log_stdout(f" ↳ Token : {new_entry_tuple[2]}\n")

        elif args.l:
            if args.json:
                entry_list = access_token_manager.listEntries()

                self.__log_json(
                    LOG_JSON_STATUS_SUCCESS,
                    "Recorded entries ID",
                    data={"entry_list": entry_list},
                )
                return

            for entries in access_token_manager.listEntries():
                self.__log_stdout(f"Entry ID {entries[0]}")
                self.__log_stdout(f" ↳ Created : {datetime.fromtimestamp(entries[1])}")
                self.__log_stdout(f" ↳ Enabled : {bool(entries[2])}\n")

        else:
            if args.delete_entry:
                if not access_token_manager.getEntry(args.delete_entry):
                    if args.json:
                        self.__log_json(
                            LOG_JSON_STATUS_ERROR,
                            f"Entry ID {args.delete_entry} does not exists on database\n",
                        )
                        return

                    self.__log_stdout(
                        f"Entry ID {args.delete_entry} does not exists on database\n"
                    )
                    return

                access_token_manager.deleteEntry(args.delete_entry)

                if args.json:
                    self.__log_json(LOG_JSON_STATUS_SUCCESS, "Entry ID was deleted\n")
                    return

            elif args.enable_entry:
                if not access_token_manager.getEntry(args.enable_entry):
                    if args.json:
                        self.__log_json(
                            LOG_JSON_STATUS_ERROR,
                            f"Entry ID {args.enable_entry} does not exists on database\n",
                        )
                        return

                    self.__log_stdout(
                        f"Entry ID {args.enable_entry} does not exists on database\n"
                    )
                    return

                access_token_manager.enableEntry(args.enable_entry)

                if args.json:
                    self.__log_json(LOG_JSON_STATUS_SUCCESS, "Entry ID was enabled")
                    return

            else:
                if args.disable_entry:
                    if not access_token_manager.getEntry(args.disable_entry):
                        if args.json:
                            self.__log_json(
                                LOG_JSON_STATUS_ERROR,
                                f"Entry ID {args.disable_entry} does not exists on database\n",
                            )
                            return

                        self.__log_stdout(
                            f"Entry ID {args.disable_entry} does not exists on database\n"
                        )
                        return

                    access_token_manager.disableEntry(args.disable_entry)

                    if args.json:
                        self.__log_json(
                            LOG_JSON_STATUS_SUCCESS, "Entry ID was disabled"
                        )
                        return

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

        new_rsa_wrapper = RSAWrapper(
            key_size=args.key_size if args.key_size else DEFAULT_RSA_KEY_SIZE
        )

        if not os.path.exists(self.config_content["paths"].get("rsa_keys_root_path")):
            self.__create_file_recursively(
                self.config_content["paths"].get("rsa_keys_root_path"), is_folder=True
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

        if args.json:
            self.__log_json(
                LOG_JSON_STATUS_SUCCESS,
                "RSA keys re-generated",
                data={
                    "fingerprint": hashlib.sha256(
                        new_rsa_wrapper.getPublicKey()
                    ).hexdigest()
                },
            )
            return

        self.__log_stdout("RSA keys re-generated")
        self.__log_stdout(
            f" ↳ Fingerprint : {hashlib.sha256(new_rsa_wrapper.getPublicKey()).hexdigest()}\n"
        )
