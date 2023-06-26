"""
    Copyright 2023 The Anweddol project
    See the LICENSE file for licensing informations
    ---

    Server installation script

"""
from setuptools import setup
from subprocess import Popen, PIPE
import shutil
import os


def checkUserExistence(username):
    with open("/etc/passwd", "r") as fd:
        if username not in fd.read():
            return False

    return True


def executeCommand(command):
    Popen(command.split(" "), shell=False, stdout=PIPE, stderr=PIPE)


print("[SETUP] Checking operating system ...")
if os.name == "nt":
    raise EnvironmentError("The Anweddol server is only available on linux systems.")

print("[SETUP] Checking permissions ...")
if os.geteuid() == 0:
    # Create needed folders
    print("[SETUP (root)] Creating folders ...")
    for path in ["/etc/anweddol", "/var/log/anweddol"]:
        if not os.path.exists(path):
            os.mkdir(path)

    # Create the configuration file
    print("[SETUP (root)] Creating configuration file ...")
    if os.path.exists("/etc/anweddol/config.yaml"):
        os.remove("/etc/anweddol/config.yaml")

    shutil.copy(
        os.path.dirname(os.path.realpath(__file__)) + "/resources/config.yaml",
        "/etc/anweddol/",
    )

    # Add the user anweddol and create ACL entries for rwx 'anweddol' user permission
    # on the /etc/anweddol directory
    print("[SETUP (root)] Creating user 'anweddol' ...")
    if checkUserExistence("anweddol"):
        executeCommand("userdel -r anweddol")

    executeCommand("useradd -s /sbin/nologin -M anweddol")
    executeCommand("usermod -a -G libvirt anweddol")
    executeCommand(
        "setfacl -m u:anweddol:rwx /etc/anweddol /var/log/anweddol/runtime.txt/"
    )

    # Create the systemctl service and enable it
    print("[SETUP (root)] Creating systemctl service ...")
    if os.path.exists("/usr/lib/systemd/system/anweddol-server.service"):
        os.remove("/usr/lib/systemd/system/anweddol-server.service")

    shutil.copy(
        os.path.dirname(os.path.realpath(__file__))
        + "/resources/anweddol-server.service",
        "/usr/lib/systemd/system/anweddol-server.service",
    )
    # executeCommand("systemctl enable anweddol-server.service")

else:
    print(
        "[SETUP] WARN : Non-root user detected, the installation limits to the 'anwdlserver' python package installation"
    )

print("[SETUP] Installing Anweddol server package ...")
setup(
    name="anwdlserver",
    version="1.0.4",
    description="The Anweddol server implementation",
    author="The Anweddol project",
    author_email="the-anweddol-project@proton.me",
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Programming Language :: Python :: 3",
        "Topic :: Internet",
        "Topic :: System :: Emulators",
    ],
    license="GPL v3",
    url="https://github.com/the-anweddol-project/Anweddol-server",
    packages=["anwdlserver", "anwdlserver.core", "anwdlserver.tools"],
    install_requires=[
        "cryptography",
        "paramiko",
        "python-daemon",
        "cerberus",
        "defusedxml",
        "sqlalchemy",
        "pyyaml",
    ],
    include_package_data=True,
    entry_points={
        "console_scripts": ["anwdlserver = anwdlserver.cli:MainAnweddolServerCLI"],
    },
)
