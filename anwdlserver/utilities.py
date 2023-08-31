import os

from .core.utilities import (
    isPortBindable,
    isInterfaceExists,
    isUserExists,
)


class Colors:
    GREEN = "\x1b[0;32;40m"
    RED = "\x1b[0;31;40m"
    ORANGE = "\x1b[0;33;40m"


def createFileRecursively(path, is_folder=False):
    try:
        os.makedirs(os.path.dirname(path) if not is_folder else path)

    except FileExistsError:
        pass

    if is_folder:
        return

    with open(path, "w") as fd:
        fd.close()


def checkServerEnvironment(config_content):
    errors_list = []

    if not isPortBindable(config_content["server"].get("listen_port")):
        errors_list.append(
            f"Port {config_content['server'].get('listen_port')} is not bindable"
        )

    if not isInterfaceExists(config_content["container"].get("nat_interface_name")):
        errors_list.append(
            f"Interface '{config_content['container'].get('nat_interface_name')}' does not exists on system"
        )

    if not isUserExists(config_content["server"].get("user")):
        errors_list.append(
            f"User '{config_content['server'].get('user')}' does not exists on system"
        )

    if not os.path.exists(config_content["container"].get("container_iso_file_path")):
        errors_list.append(
            f"{config_content['container'].get('container_iso_file_path')} was not found on system"
        )

    return errors_list
