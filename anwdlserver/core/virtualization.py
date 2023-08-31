"""
	Copyright 2023 The Anweddol project
	See the LICENSE file for licensing informations
	---

	Virtualization management and utilities, using libvirt API

"""
from defusedxml.minidom import parseString
import paramiko
import secrets
import hashlib
import libvirt
import random
import string
import uuid
import json
import time
import os


# Default parameters
DEFAULT_LIBVIRT_DRIVER_URI = "qemu:///system"

DEFAULT_CONTAINER_ENDPOINT_USERNAME = "endpoint"
DEFAULT_CONTAINER_ENDPOINT_PASSWORD = "endpoint"
DEFAULT_CONTAINER_ENDPOINT_LISTEN_PORT = 22

DEFAULT_NAT_INTERFACE_NAME = "virbr0"

DEFAULT_CONTAINER_MAX_TRYOUT = 20
DEFAULT_CONTAINER_MEMORY = 2048
DEFAULT_CONTAINER_VCPUS = 2

DEFAULT_CONTAINER_CLIENT_SSH_PASSWORD_LENGTH = 120

DEFAULT_CONTAINER_WAIT_AVAILABLE = True
DEFAULT_STORE_CONTAINER = True
DEFAULT_STORE_CREDENTIALS = True
DEFAULT_STOP_CONTAINER_DOMAIN = False


# Represents an established SSH tunnel between the server and a container domain
class EndpointShellInstance:
    def __init__(
        self,
        container_ip: str,
        endpoint_username: str = DEFAULT_CONTAINER_ENDPOINT_USERNAME,
        endpoint_password: str = DEFAULT_CONTAINER_ENDPOINT_PASSWORD,
        endpoint_listen_port: int = DEFAULT_CONTAINER_ENDPOINT_LISTEN_PORT,
    ):
        self.container_ip = container_ip

        self.stored_client_ssh_uername = None
        self.stored_client_ssh_password = None

        self.endpoint_username = endpoint_username
        self.endpoint_password = endpoint_password
        self.endpoint_listen_port = endpoint_listen_port

        self.ssh_client = None

    def __del__(self):
        if self.ssh_client:
            self.closeShell()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        if self.ssh_client:
            self.closeShell()

    def isClosed(self) -> bool:
        return True if not self.ssh_client else False

    def getSSHClient(self) -> paramiko.client.SSHClient:
        return self.ssh_client

    def getContainerIP(self) -> str:
        return self.container_ip

    def getEndpointCredentials(self) -> tuple:
        return (
            self.endpoint_username,
            self.endpoint_password,
            self.endpoint_listen_port,
        )

    def getStoredClientSSHCredentials(self) -> tuple:
        return (
            self.stored_client_ssh_uername,
            self.stored_client_ssh_password,
        )

    def setContainerIP(self, ip: str) -> None:
        self.container_ip = ip

    def setEndpointCredentials(
        self, username: str, password: str, listen_port: int
    ) -> None:
        self.endpoint_username = username
        self.endpoint_password = password
        self.endpoint_listen_port = listen_port

    def storeClientSSHCredentials(
        self,
        client_ssh_uername: str,
        client_ssh_password: str,
    ) -> None:
        self.stored_client_ssh_uername = client_ssh_uername
        self.stored_client_ssh_password = client_ssh_password

    def openShell(self) -> None:
        if self.ssh_client is not None:
            RuntimeError("Endpoint shell is already opened")

        self.ssh_client = paramiko.client.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh_client.connect(
            self.container_ip,
            self.endpoint_listen_port,
            username=self.endpoint_username,
            password=self.endpoint_password,
        )

    def administrateContainer(self) -> None:
        if not self.ssh_client:
            raise RuntimeError("Endpoint shell is not open")

        _stdout, _stderr = self.executeCommand(
            "sudo /bin/anweddol_container_setup.sh {} {} 22".format(
                self.stored_client_ssh_uername,
                self.stored_client_ssh_password,
            )
        )

        if _stdout or _stderr:
            raise RuntimeError(f"Failed to set SSH credentials : {_stdout} | {_stderr}")

    def executeCommand(self, command: str) -> tuple:
        _, _stdout, _stderr = self.ssh_client.exec_command(command)

        return (_stdout.read().decode(), _stderr.read().decode())

    def generateClientSSHCredentials(
        self,
        password_lenght: int = DEFAULT_CONTAINER_CLIENT_SSH_PASSWORD_LENGTH,
        store: bool = DEFAULT_STORE_CREDENTIALS,
    ) -> tuple:
        username = f"user_{random.SystemRandom().randint(10000, 90000)}"
        password = "".join(
            secrets.choice(string.ascii_letters + string.digits)
            for x in range(password_lenght)
        )

        if store:
            self.stored_client_ssh_uername = username
            self.stored_client_ssh_password = password

        return (username, password)

    def closeShell(self) -> None:
        self.ssh_client.close()
        self.ssh_client = None


# Represents a container and its management functionnalities
class ContainerInstance:
    def __init__(
        self,
        iso_file_path: str = None,
        container_uuid: str = None,
        nat_interface_name: str = DEFAULT_NAT_INTERFACE_NAME,
        memory: int = DEFAULT_CONTAINER_MEMORY,
        vcpus: int = DEFAULT_CONTAINER_VCPUS,
    ):
        self.iso_file_path = os.path.abspath(iso_file_path) if iso_file_path else None
        self.uuid = container_uuid if container_uuid else str(uuid.uuid4())
        self.nat_interface_name = nat_interface_name
        self.memory = memory
        self.vcpus = vcpus

        self.domain_descriptor = None

    def __del__(self):
        if self.isDomainRunning():
            self.stopDomain()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        if traceback and self.isDomainRunning():
            self.stopDomain()

    def isDomainRunning(self) -> bool:
        if self.domain_descriptor is None:
            return False

        return self.domain_descriptor.isActive()

    def getNATInterfaceName(self) -> str:
        return self.nat_interface_name

    def getDomainDescriptor(self) -> None | libvirt.virDomain:
        return self.domain_descriptor

    def getUUID(self) -> str:
        return self.uuid

    def getISOFilePath(self) -> str:
        return self.iso_file_path

    def getMAC(self) -> None | str:
        if self.domain_descriptor is None:
            raise RuntimeError("Container domain is not created")

        # Get the container MAC address
        container_domain_xml = parseString(self.domain_descriptor.XMLDesc(0))
        return container_domain_xml.getElementsByTagName("mac")[0].getAttribute(
            "address"
        )

    # @TODO To test : https://libvirt.gitlab.io/libvirt-appdev-guide-python/libvirt_application_development_guide_using_python-Network_Interface-Addresses.html
    def getIP(self) -> None | str:
        if self.domain_descriptor is None:
            raise RuntimeError("Container domain is not created")

        container_mac_address = self.getMAC()

        # Get the content of the interface file to get its IP
        with open(
            f"/var/lib/libvirt/dnsmasq/{self.nat_interface_name}.status", "r"
        ) as fd:
            status_content = fd.read()

        if container_mac_address not in status_content:
            return

        for container_net_info in json.loads(status_content):
            if container_net_info["mac-address"] != container_mac_address:
                continue

            return container_net_info.get("ip-address")

    def getMemory(self) -> int:
        return self.memory

    def getVCPUs(self) -> int:
        return self.vcpus

    def setDomainDescriptor(self, domain_descriptor: libvirt.virDomain) -> None:
        self.domain_descriptor = domain_descriptor

    def setISOFilePath(self, iso_file_path: str) -> None:
        self.iso_file_path = os.path.abspath(iso_file_path)

    def setMemory(self, memory: int) -> None:
        self.memory = memory

    def setVCPUs(self, vcpus: int) -> None:
        self.vcpus = vcpus

    def setNATInterfaceName(self, nat_interface_name: str) -> None:
        self.nat_interface_name = nat_interface_name

    def makeISOFileChecksum(self) -> str:
        hasher = hashlib.sha256()

        with open(self.iso_file_path, "rb") as fd:
            hasher.update(fd.read())

        return hasher.hexdigest()

    def createEndpointShell(
        self,
        endpoint_username: str = DEFAULT_CONTAINER_ENDPOINT_USERNAME,
        endpoint_password: str = DEFAULT_CONTAINER_ENDPOINT_PASSWORD,
        endpoint_listen_port: int = DEFAULT_CONTAINER_ENDPOINT_LISTEN_PORT,
    ) -> EndpointShellInstance:
        if not self.isDomainRunning():
            raise RuntimeError("Container domain is not running")

        return EndpointShellInstance(
            self.getIP(), endpoint_username, endpoint_password, endpoint_listen_port
        )

    def startDomain(
        self,
        wait_available: bool = DEFAULT_CONTAINER_WAIT_AVAILABLE,
        wait_max_tryout: int = DEFAULT_CONTAINER_MAX_TRYOUT,
        driver_uri: str = DEFAULT_LIBVIRT_DRIVER_URI,
    ) -> None:
        if self.isDomainRunning():
            raise RuntimeError("Container domain is already running")

        if not self.iso_file_path:
            raise ValueError("Container domain ISO file path is not set")

        hypervisor_connection = libvirt.open(driver_uri)

        try:
            new_domain_xml = f"""
    			<domain type='kvm'>
    				<name>{self.uuid}</name>
    				<memory unit='MiB'>{self.memory}</memory>
    				<vcpu placement='static'>{self.vcpus}</vcpu>
    				<uuid>{self.uuid}</uuid>
    				<os>
    					<type arch='x86_64' machine='pc'>hvm</type>
    					<boot dev='hd'/>
    					<boot dev='cdrom'/>
    				</os>
    				<features>
    					<acpi/>
    					<apic/>
    					<vmport state='off'/>
    				</features>
    				<clock offset='utc'>
    					<timer name='rtc' tickpolicy='catchup'/>
    					<timer name='pit' tickpolicy='delay'/>
    					<timer name='hpet' present='no'/>
    				</clock>
    				<pm>
    					<suspend-to-mem enabled='yes'/>
    					<suspend-to-disk enabled='yes'/>
    				</pm>
    				<devices>
    					<disk type='file' device='cdrom'>
    						<driver name='qemu' type='raw'/>
    						<source file='{self.iso_file_path}'/>
    						<target dev='hda' bus='ide'/>
    						<address type='drive' controller='0' bus='0' target='0' unit='0'/>
    					</disk>
    					<interface type='bridge'>
    				        <start mode='onboot'/>
    				        <source bridge='{self.nat_interface_name}'/> 
    				        <model type='virtio'/>
    				    </interface>
                        <memballoon model='virtio'>
    						<address type='pci' domain='0x0000' bus='0x00' slot='0x07' function='0x0'/>
    					</memballoon>
    				</devices>
    			</domain>"""

            self.domain_descriptor = hypervisor_connection.defineXML(new_domain_xml)
            self.domain_descriptor.create()

            if wait_available:
                tryout_counter = wait_max_tryout

                while tryout_counter != 0:
                    if self.getIP():
                        break

                    time.sleep(1)
                    tryout_counter -= 1

                if tryout_counter == 0:
                    raise TimeoutError(
                        "Maximum try amount was reached while trying to get container domain IP"
                    )

            hypervisor_connection.close()

        except Exception as E:
            hypervisor_connection.close()
            raise E

    def stopDomain(self) -> None:
        if not self.isDomainRunning():
            raise RuntimeError("Container domain is not running")

        self.domain_descriptor.destroy()


class VirtualizationInterface:
    def __init__(self):
        self.stored_container_instance_dict = {}

    def __del__(self):
        for stored_container in self.stored_container_instance_dict:
            if stored_container.isDomainRunning():
                stored_container.stopDomain()

            self.deleteStoredContainer(stored_container.getUUID())

    def getStoredContainersAmount(self) -> int:
        return len(self.listStoredContainers())

    def listStoredContainers(self) -> list:
        return self.stored_container_instance_dict.keys()

    def getStoredContainer(self, container_uuid: str) -> None | ContainerInstance:
        return self.stored_container_instance_dict.get(container_uuid)

    def storeContainer(self, container_instance: ContainerInstance) -> None:
        if container_instance.getUUID() in self.listStoredContainers():
            raise ValueError("A container already exists under the same UUID")

        self.stored_container_instance_dict.update(
            {container_instance.getUUID(): container_instance}
        )

    def createContainer(
        self, store: bool = DEFAULT_STORE_CONTAINER
    ) -> ContainerInstance:
        new_container_interface = ContainerInstance()

        if store:
            self.addStoredContainer(new_container_interface)

        return new_container_interface

    def deleteStoredContainer(
        self,
        container_uuid: str,
        stop_container_domain: bool = DEFAULT_STOP_CONTAINER_DOMAIN,
    ) -> None:
        if stop_container_domain:
            container_instance = self.getStoredContainer()

            if container_instance and container_instance.isDomainRunning():
                container_instance.stopDomain()

        self.stored_container_instance_dict.pop(container_uuid, None)
