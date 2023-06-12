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
    try:
        data = socket_descriptor.recv(16, socket.MSG_DONTWAIT | socket.MSG_PEEK)
        return len(data) == 0

    except OSError:
        return False

    except BlockingIOError:
        return False

    except ConnectionResetError:
        return True


def isValidIP(ip: str) -> bool:
    if not re.search(r"^\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b$", ip):
        return False

    try:
        socket.inet_aton(ip)
        return True

    except Exception:
        return False


def isInterfaceExists(interface_name: str) -> bool:
    stdout, stderr = Popen(["/sbin/ip", "a"], stdout=PIPE, shell=False).communicate()
    if interface_name not in stdout.decode():
        return False

    return True


def isUserExists(username: str) -> bool:
    with open("/etc/passwd", "r") as fd:
        if username not in fd.read():
            return False

    return True
