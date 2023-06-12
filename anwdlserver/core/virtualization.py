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

# Intern importation
from .util import isPortBindable


# Default parameters
DEFAULT_LIBVIRT_DRIVER_URI = "qemu:///system"

DEFAULT_CONTAINER_ENDPOINT_USERNAME = "endpoint"
DEFAULT_CONTAINER_ENDPOINT_PASSWORD = "endpoint"
DEFAULT_CONTAINER_ENDPOINT_LISTEN_PORT = 22

DEFAULT_BRIDGE_INTERFACE_NAME = "anwdlbr0"
DEFAULT_NAT_INTERFACE_NAME = "virbr0"

DEFAULT_CONTAINER_MAX_TRYOUT = 20
DEFAULT_MAX_ALLOWED_CONTAINERS = 6
DEFAULT_CONTAINER_MEMORY = 2048
DEFAULT_CONTAINER_VCPUS = 2

DEFAULT_CONTAINER_PORT_RANGE = range(10000, 15000)

DEFAULT_CONTAINER_WAIT_AVAILABLE = True
DEFAULT_CONTAINER_DESTROY_DOMAIN = True
DEFAULT_STORE_CONTAINER = True


# Represents an established SSH tunnel between the server and a container
class EndpointShellInstance:
    def __init__(self, ssh_client: paramiko.client.SSHClient):
        self.ssh_client = ssh_client
        self.stored_container_ssh_credentials = None
        self.is_closed = False

    def __del__(self):
        if not self.is_closed:
            self.closeShell()

    def isClosed(self) -> bool:
        return self.is_closed

    def getSSHClient(self) -> paramiko.client.SSHClient:
        return self.ssh_client

    def getStoredContainerSSHCredentials(self) -> tuple:
        return self.stored_container_ssh_credentials

    def executeCommand(self, command: str) -> tuple:
        _stdin, _stdout, _stderr = self.ssh_client.exec_command(command)

        return (_stdout.read().decode(), _stderr.read().decode())

    def generateContainerSSHCredentials(
        self,
        port_range: range = DEFAULT_CONTAINER_PORT_RANGE,
    ) -> tuple:
        username = f"user_{random.SystemRandom().randint(10000, 90000)}"
        password = "".join(
            secrets.choice(string.ascii_letters + string.digits) for x in range(120)
        )

        while 1:
            listen_port = random.SystemRandom().choice(port_range)
            if not isPortBindable(listen_port):
                continue

            break

        return (username, password, listen_port)

    def setContainerSSHCredentials(
        self, username: str, password: str, listen_port: int
    ) -> None:
        output_tuple = self.executeCommand(
            "sudo /bin/anweddol_container_setup.sh {} {} {}".format(
                username,
                password,
                listen_port,
            )
        )

        if output_tuple[0] or output_tuple[1]:
            raise RuntimeError(f"Failed to set SSH credentials : {output_tuple}")

        self.stored_container_ssh_credentials = (username, password, listen_port)

        self.closeShell()

    def closeShell(self) -> None:
        self.ssh_client.close()
        self.is_closed = True


# Represents a container and its management functionnalities
class ContainerInstance:
    def __init__(
        self,
        uuid: str,
        iso_path: str,
        memory: int = DEFAULT_CONTAINER_MEMORY,
        vcpus: int = DEFAULT_CONTAINER_VCPUS,
        nat_interface_name: str = DEFAULT_NAT_INTERFACE_NAME,
        bridge_interface_name: str = DEFAULT_BRIDGE_INTERFACE_NAME,
        endpoint_username: str = DEFAULT_CONTAINER_ENDPOINT_USERNAME,
        endpoint_password: str = DEFAULT_CONTAINER_ENDPOINT_PASSWORD,
        endpoint_listen_port: int = DEFAULT_CONTAINER_ENDPOINT_LISTEN_PORT,
    ):
        self.uuid = uuid
        self.iso_path = os.path.abspath(iso_path)
        self.memory = memory
        self.vcpus = vcpus
        self.nat_interface_name = nat_interface_name
        self.bridge_interface_name = bridge_interface_name
        self.endpoint_username = endpoint_username
        self.endpoint_password = endpoint_password
        self.endpoint_listen_port = endpoint_listen_port
        self.domain_descriptor = None

    def isDomainRunning(self) -> bool:
        if self.domain_descriptor is None:
            return False

        return self.domain_descriptor.isActive()

    def getNATInterfaceName(self) -> str:
        return self.nat_interface_name

    def getBridgeInterfaceName(self) -> str:
        return self.bridge_interface_name

    def getDomainDescriptor(self) -> None | libvirt.virDomain:
        return self.domain_descriptor

    def getUUID(self) -> str:
        return self.uuid

    def getISOPath(self) -> str:
        return self.iso_path

    def getMAC(self) -> None | str:
        if self.domain_descriptor is None:
            raise RuntimeError("Container domain is not created")

        # Get the container MAC address
        container_domain_xml = parseString(self.domain_descriptor.XMLDesc(0))
        return container_domain_xml.getElementsByTagName("mac")[0].getAttribute(
            "address"
        )

    def getIP(self) -> None | str:
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

    def setISOPath(self, iso_path: str) -> None:
        self.iso_path = iso_path

    def setMemory(self, memory: int) -> None:
        self.memory = memory

    def setVCPUs(self, vcpus: int) -> None:
        self.vcpus = vcpus

    def setNATInterfaceName(self, nat_interface_name: str) -> None:
        self.nat_interface_name = nat_interface_name

    def setBridgeInterfaceName(self, bridge_interface_name: str) -> None:
        self.bridge_interface_name = bridge_interface_name

    def setEndpointSSHAuthenticationCredentials(
        self,
        endpoint_username: str = DEFAULT_CONTAINER_ENDPOINT_USERNAME,
        endpoint_password: str = DEFAULT_CONTAINER_ENDPOINT_PASSWORD,
        endpoint_listen_port: str = DEFAULT_CONTAINER_ENDPOINT_LISTEN_PORT,
    ) -> None:
        self.endpoint_username = endpoint_username
        self.endpoint_password = endpoint_password
        self.endpoint_listen_port = endpoint_listen_port

    def makeISOChecksum(self) -> str:
        hasher = hashlib.sha256()

        with open(self.iso_path, "rb") as fd:
            hasher.update(fd.read())

        return hasher.hexdigest()

    def createEndpointShell(self) -> EndpointShellInstance:
        if not self.isDomainRunning():
            raise RuntimeError("Container domain is not running")

        container_ssh_client = paramiko.client.SSHClient()
        container_ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        container_ssh_client.connect(
            self.getIP(),
            self.endpoint_listen_port,
            username=self.endpoint_username,
            password=self.endpoint_password,
        )

        return EndpointShellInstance(container_ssh_client)

    def startDomain(
        self,
        wait_available: bool = DEFAULT_CONTAINER_WAIT_AVAILABLE,
        wait_max_tryout: int = DEFAULT_CONTAINER_MAX_TRYOUT,
        driver_uri: str = DEFAULT_LIBVIRT_DRIVER_URI,
    ) -> None:
        if self.isDomainRunning():
            raise RuntimeError("Container domain is already running")

        hypervisor_connection = libvirt.open(driver_uri)

        try:
            new_domain_xml = f"""
    			<domain type='kvm'>
    				<name>{self.uuid}</name>
    				<memory unit='MiB'>{self.memory}</memory>
    				<currentMemory unit='MiB'>{self.memory}</currentMemory>
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
    						<source file='{self.iso_path}'/>
    						<target dev='hda' bus='ide'/>
    						<address type='drive' controller='0' bus='0' target='0' unit='0'/>
    					</disk>
    					<interface type='bridge'>
    				        <start mode='onboot'/>
    				        <source bridge='{self.nat_interface_name}'/> 
    				        <model type='virtio'/>
    				    </interface>
                        <interface type='bridge'>
                            <start mode='onboot'/>
                            <source bridge='{self.bridge_interface_name}'/>
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

        except Exception as E:
            hypervisor_connection.close()
            raise E

    def stopDomain(self, destroy: bool = DEFAULT_CONTAINER_DESTROY_DOMAIN) -> None:
        if not self.isDomainRunning():
            raise RuntimeError("Container domain is not running")

        self.domain_descriptor.destroy() if destroy else self.domain_descriptor.shutdown()


class VirtualizationInterface:
    def __init__(
        self,
        container_iso_path: str,
        max_allowed_containers: int = DEFAULT_MAX_ALLOWED_CONTAINERS,
    ):
        self.container_iso_path = os.path.abspath(container_iso_path)
        self.max_allowed_containers = max_allowed_containers

        self.stored_container_instance_dict = {}
        self.running_containers_counter = 0

    def getIsoPath(self) -> str:
        return self.container_iso_path

    def getMaxAllowedContainersAmount(self) -> int:
        return self.max_allowed_containers

    def getContainersAmount(self) -> int:
        return self.running_containers_counter

    def getAvailableContainersAmount(self) -> int:
        return self.getMaxAllowedContainersAmount() - self.getContainersAmount()

    def listStoredContainers(self) -> list:
        return self.stored_container_instance_dict.keys()

    def getStoredContainer(self, container_uuid: str) -> None | ContainerInstance:
        return self.stored_container_instance_dict.get(container_uuid)

    def setIsoPath(self, container_iso_path: str) -> None:
        self.container_iso_path = os.path.abspath(container_iso_path)

    def setMaxAllowedContainers(self, max_allowed_containers: int) -> None:
        self.max_allowed_containers = max_allowed_containers

    def addStoredContainer(self, container_instance: ContainerInstance) -> None:
        if self.running_containers_counter >= self.max_allowed_containers:
            raise RuntimeError("Running containers maximum amount was reached")

        self.stored_container_instance_dict.update(
            {container_instance.getUUID(): container_instance}
        )

        self.running_containers_counter += 1

    def deleteStoredContainer(self, container_uuid: str) -> None:
        self.stored_container_instance_dict.pop(container_uuid)

        self.running_containers_counter -= 1

    def createContainer(
        self, store: bool = DEFAULT_STORE_CONTAINER
    ) -> ContainerInstance:
        new_container_uuid = str(uuid.uuid4())
        new_container_interface = ContainerInstance(
            new_container_uuid, self.container_iso_path
        )

        if store:
            self.addStoredContainer(new_container_interface)

        return new_container_interface
