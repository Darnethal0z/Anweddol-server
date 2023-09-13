"""
    Copyright 2023 The Anweddol project
    See the LICENSE file for licensing informations
    ---

    CLI : Configuration file management features

"""
import cerberus
import yaml

# Intern importation
from .core.utilities import isValidIP


def loadConfigurationFileContent(config_file_path, auto_check=True) -> None | dict:
    with open(config_file_path, "r") as fd:
        data = yaml.safe_load(fd)

    def __check_valid_ip(field, value, error):
        if value == "any":
            return

        if not isValidIP(value):
            error(field, f"{value} is not a valid IPv4 format")

    def __check_port_range(field, value, error):
        min_port, max_port = value

        if min_port < 1 or min_port > 65535:
            error(field, f"{min_port} is not a valid port")

        if max_port < 1 or max_port > 65535:
            error(field, f"{max_port} is not a valid port")

        if len(range(min_port, max_port)) < data["container"].get(
            "max_allowed_running_container_domains"
        ):
            error(
                field,
                "Port range is smaller than minimum allowed running containers amount",
            )

    validator_schema_dict = {
        "container": {
            "type": "dict",
            "require_all": True,
            "schema": {
                "container_iso_file_path": {"type": "string"},
                "max_allowed_running_container_domains": {
                    "type": "integer",
                    "nullable": True,
                    "min": 1,
                },
                "container_memory": {
                    "type": "integer",
                    "min": 256,
                },
                "container_vcpus": {"type": "integer", "min": 1},
                "nat_interface_name": {"type": "string"},
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
                "public_rsa_key_file_path": {"type": "string"},
                "private_rsa_key_file_path": {"type": "string"},
                "log_file_path": {"type": "string"},
                "pid_file_path": {"type": "string"},
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
                "timeout": {"type": "integer", "nullable": True, "min": 1},
                "enable_onetime_rsa_keys": {"type": "boolean"},
            },
        },
        "port_forwarding": {
            "type": "dict",
            "require_all": True,
            "schema": {
                "port_range": {"type": "list", "check_with": __check_port_range},
            },
        },
        "log_rotation": {
            "type": "dict",
            "require_all": True,
            "schema": {
                "enabled": {"type": "boolean"},
                "log_archive_folder_path": {"type": "string"},
                "max_log_lines_amount": {"type": "integer", "min": 1},
                "action": {"type": "string", "allowed": ["delete", "archive"]},
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
                "access_token_database_file_path": {"type": "string"},
                "enabled": {"type": "boolean"},
            },
        },
    }

    validator = cerberus.Validator(purge_unknown=True)

    if not validator.validate(data, validator_schema_dict):
        return (False, validator.errors)

    return (True, validator.document)
