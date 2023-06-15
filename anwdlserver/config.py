"""
    Copyright 2023 The Anweddol project
    See the LICENSE file for licensing informations
    ---

    CLI : Configuration file management features

"""
from urllib.parse import urlparse
from psutil import virtual_memory
import cerberus
import yaml

# Intern importation
from .core.util import isValidIP


class ConfigurationFileManager:
    def __init__(self, config_file_path):
        self.config_file_path = config_file_path

    # See the Cerberus docs : https://docs.python-cerberus.org/en/stable/usage.html
    def loadContent(self, auto_check: bool = True) -> None | dict:
        with open(self.config_file_path, "r") as fd:
            data = yaml.safe_load(fd)

        def __check_valid_ip(field, value, error):
            if value == "any":
                return

            if not isValidIP(value):
                error(field, f"{value} is not a valid IPv4 format")

        def __check_valid_url(field, value, error):
            if field == "container_iso_mirror_url" and not value:
                return

            url_check = urlparse(value)
            if not url_check.geturl():
                error(field, f"{value} is not a valid URL format")

        validator_schema_dict = {
            "paths": {
                "type": "dict",
                "require_all": True,
                "schema": {
                    "log_file_path": {"type": "string"},
                    "pid_file_path": {"type": "string"},
                    "container_iso_path": {"type": "string"},
                    "rsa_keys_root_path": {"type": "string"},
                    "access_tokens_database_path": {"type": "string"},
                },
            },
            "container": {
                "type": "dict",
                "require_all": True,
                "schema": {
                    "max_allowed_running_containers": {"type": "integer", "min": 1},
                    # Get the available memory in megabytes
                    # (does not consider swap memory)
                    "container_memory": {
                        "type": "integer",
                        "min": 1,
                        "max": virtual_memory().available / 1000000,
                    },
                    "container_vcpus": {"type": "integer", "min": 1},
                    "nat_interface_name": {"type": "string"},
                    "bridge_interface_name": {"type": "string"},
                    "endpoint_username": {"type": "string"},
                    "endpoint_password": {"type": "string"},
                    "endpoint_listen_port": {
                        "type": "integer",
                        "min": 1,
                        "max": 65535,
                    },
                },
            },
            "server": {
                "type": "dict",
                "require_all": True,
                "schema": {
                    "user": {"type": "string"},
                    "bind_address": {
                        "type": "string",
                        "maxlength": 15,
                        "check_with": __check_valid_ip,
                    },
                    "listen_port": {
                        "type": "integer",
                        "min": 1,
                        "max": 65535,
                    },
                    "timeout": {"type": "integer", "min": 0},
                    "enable_onetime_rsa_keys": {"type": "boolean"},
                },
            },
            "ip_filter": {
                "type": "dict",
                "require_all": True,
                "schema": {
                    "enabled": {"type": "boolean"},
                    "allowed_ip_list": {
                        "type": "list",
                        "schema": {"type": "string", "check_with": __check_valid_ip},
                    },
                    "denied_ip_list": {
                        "type": "list",
                        "schema": {"type": "string", "check_with": __check_valid_ip},
                    },
                },
            },
            "access_token": {
                "type": "dict",
                "require_all": True,
                "schema": {
                    "enabled": {"type": "boolean"},
                },
            },
        }

        validator = cerberus.Validator(purge_unknown=True)

        if not validator.validate(data, validator_schema_dict):
            return (False, validator.errors)

        return (True, validator.document)
