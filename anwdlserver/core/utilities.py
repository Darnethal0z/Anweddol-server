"""
    Copyright 2023 The Anweddol project
    See the LICENSE file for licensing informations
    ---

    Miscellaneous features

    NOTE : Some functions be hard to debug with the several except statements, 
    please considerate this function when implementing a new experimental feature 

"""
from subprocess import Popen, PIPE
import socket
import re


def isPortBindable(port: int) -> bool:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        sock.bind(("", port))
        sock.close()
        return True

    except OSError:
        sock.close()
        return False


def isSocketClosed(socket_descriptor: socket.socket) -> bool:
    return socket_descriptor.fileno() == -1


def isValidIP(ip: str) -> bool:
    if not re.search(r"^\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b$", ip):
        return False

    try:
        socket.inet_aton(ip)
        return True

    except Exception:
        return False


def isInterfaceExists(interface_name: str) -> bool:
    _stdout, _ = Popen(
        ["/sbin/ip", "a"], stdout=PIPE, stderr=PIPE, shell=False
    ).communicate()
    return interface_name in _stdout.decode()


def isUserExists(username: str) -> bool:
    with open("/etc/passwd", "r") as fd:
        return username in fd.read()
