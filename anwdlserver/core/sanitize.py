"""
    Copyright 2023 The Anweddol project
    See the LICENSE file for licensing informations
    ---

    Normalized request / response values and formats

"""
import cerberus
import re


def verifyRequestContent(request_dict: dict) -> tuple:
    validator = cerberus.Validator()
    validator.allow_unknown = True

    def __check_container_uuid(field, value, error):
        if not re.search(
            r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", value
        ):
            error(
                field,
                "value does not match regex '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'",
            )

    def __check_client_token(field, value, error):
        if not re.search(r"^[0-9a-zA-Z-_]{255}$", value):
            error(field, "value does not match regex '^[0-9a-zA-Z-_]{255}$'")

    request_verification_scheme = {
        "verb": {
            "type": "string",
            "regex": r"^[A-Z]{1,}$",
            "required": True,
        },
        "parameters": {
            "type": "dict",
            "required": True,
            "schema": {
                "container_uuid": {
                    "type": "string",
                    "required": False,
                    "check_with": __check_container_uuid,
                    "dependencies": ["client_token"],
                },
                "client_token": {
                    "type": "string",
                    "required": False,
                    "check_with": __check_client_token,
                    "dependencies": ["container_uuid"],
                },
            },
        },
    }

    if not validator.validate(request_dict, request_verification_scheme):
        return (False, validator.errors)

    return (True, validator.document)


def makeResponse(
    success: bool, message: str, data: dict = {}, reason: str = None
) -> tuple:
    response_dict = {
        "success": success,
        "message": message + (f" ({reason})" if reason else ""),
        "data": data,
    }
    validator = cerberus.Validator()
    validator.allow_unknown = True

    response_verification_scheme = {
        "success": {
            "type": "boolean",
            "required": True,
        },
        "message": {
            "type": "string",
            "required": True,
        },
        "data": {
            "type": "dict",
            "required": True,
            "schema": {
                "container_uuid": {
                    "type": "string",
                    "regex": r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
                    "required": False,
                    "dependencies": [
                        "client_token",
                        "container_iso_sha256",
                        "container_username",
                        "container_password",
                        "container_listen_port",
                    ],
                },
                "client_token": {
                    "type": "string",
                    "regex": r"^[0-9a-zA-Z-_]{255}$",
                    "required": False,
                    "dependencies": [
                        "container_uuid",
                        "container_iso_sha256",
                        "container_username",
                        "container_password",
                        "container_listen_port",
                    ],
                },
                "container_iso_sha256": {
                    "type": "string",
                    "regex": r"^[a-f0-9]{64}$",
                    "required": False,
                    "dependencies": [
                        "container_uuid",
                        "client_token",
                        "container_username",
                        "container_password",
                        "container_listen_port",
                    ],
                },
                "container_username": {
                    "type": "string",
                    "regex": r"^user_[0-9]{5}$",
                    "required": False,
                    "dependencies": [
                        "container_uuid",
                        "client_token",
                        "container_iso_sha256",
                        "container_password",
                        "container_listen_port",
                    ],
                },
                "container_password": {
                    "type": "string",
                    "regex": r"^[a-zA-Z0-9]{1,}$",
                    "required": False,
                    "dependencies": [
                        "container_uuid",
                        "client_token",
                        "container_iso_sha256",
                        "container_username",
                        "container_listen_port",
                    ],
                },
                "container_listen_port": {
                    "type": "integer",
                    "required": False,
                    "min": 1,
                    "max": 65535,
                    "dependencies": [
                        "container_uuid",
                        "client_token",
                        "container_iso_sha256",
                        "container_username",
                        "container_password",
                    ],
                },
                "uptime": {
                    "type": "integer",
                    "required": False,
                    "min": 0,
                    "dependencies": ["available"],
                },
                "available": {
                    "type": "integer",
                    "required": False,
                    "min": 0,
                    "dependencies": ["uptime"],
                },
            },
        },
    }

    if not validator.validate(response_dict, response_verification_scheme):
        return (False, validator.errors)

    return (True, validator.document)
