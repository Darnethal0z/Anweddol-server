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


def executeCommand(command):
    Popen(command.split(" "), shell=False, stdout=PIPE, stderr=PIPE)


def getReadmeContent():
    with open("README.md", "r") as fd:
        return fd.read()


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
        "/etc/anweddol/config.yaml",
    )

    print("[SETUP (root)] Creating uninstallation script ...")
    shutil.copy(
        os.path.dirname(os.path.realpath(__file__))
        + "/resources/anwdlserver-uninstall",
        "/usr/local/bin/anwdlserver-uninstall",
    )
    executeCommand("chmod +x /usr/local/bin/anwdlserver-uninstall")

    # Add the user anweddol and rwx 'anweddol' user permission
    # on the /etc/anweddol and the /var/log/anweddol directory
    print("[SETUP (root)] Creating user 'anweddol' ...")
    executeCommand("useradd -s /sbin/nologin -M anweddol")
    executeCommand("usermod -aG libvirt anweddol")

    executeCommand("chown root.anweddol /etc/anweddol /var/log/anweddol")
    executeCommand("chmod -R g+rwX /etc/anweddol /var/log/anweddol")

    # Create the systemctl service and enable it
    print("[SETUP (root)] Creating systemctl service ...")
    if os.path.exists("/usr/lib/systemd/system/anweddol-server.service"):
        os.remove("/usr/lib/systemd/system/anweddol-server.service")

    shutil.copy(
        os.path.dirname(os.path.realpath(__file__))
        + "/resources/anweddol-server.service",
        "/usr/lib/systemd/system/anweddol-server.service",
    )

else:
    print(
        "[SETUP] WARN : Non-root user detected, the installation limits to the 'anwdlserver' python package installation"
    )

print("[SETUP] Installing Anweddol server package ...")
setup(
    name="anwdlserver",
    version="1.1.6",
    author="The Anweddol project",
    author_email="the-anweddol-project@proton.me",
    url="https://the-anweddol-project.github.io/",
    description="The Anweddol server implementation",
    long_description=getReadmeContent(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Programming Language :: Python :: 3",
        "Operating System :: POSIX",
        "Topic :: Internet",
        "Topic :: System :: Emulators",
    ],
    license="GPL v3",
    packages=["anwdlserver", "anwdlserver.core", "anwdlserver.tools"],
    install_requires=[
        "cryptography",
        "paramiko",
        "python-daemon",
        "cerberus",
        "defusedxml",
        "sqlalchemy",
        "pyyaml",
        "psutil",
    ],
    include_package_data=True,
    entry_points={
        "console_scripts": ["anwdlserver = anwdlserver.cli:MainAnweddolServerCLI"],
    },
)
