from subprocess import Popen, DEVNULL
import random
import time

from .utilities import isPortBindable

# Default values
DEFAULT_STORE_FORWARDER = True
DEFAULT_STOP_FORWARD = False
DEFAULT_FORWARDABLE_PORT_RANGE = range(10000, 15000)


# Inspired from https://github.com/Dronehub/socatlord/blob/master/socatlord/operations.py
class ForwarderInstance:
    def __init__(
        self,
        server_origin_port: int,
        container_ip: str,
        container_destination_port: int,
    ):
        self.server_origin_port = server_origin_port
        self.container_ip = container_ip
        self.container_destination_port = container_destination_port

        self.process = None

    def __del__(self):
        if self.process:
            self.stopForward()

    def isForwarding(self) -> bool:
        return (self.process.poll() is None) if self.process else False

    def getServerOriginPort(self) -> int:
        return self.server_origin_port

    def getContainerIP(self) -> str:
        return self.container_ip

    def getContainerDestinationPort(self) -> int:
        return self.container_destination_port

    def getProcess(self) -> Popen:
        return self.process

    def setServerOriginPort(self, server_origin_port: int) -> None:
        self.server_origin_port = server_origin_port

    def setContainerIP(self, container_ip: str) -> None:
        self.container_ip = container_ip

    def setContainerDestinationPort(self, container_destination_port: int) -> None:
        self.container_destination_port = container_destination_port

    def setProcess(self, process: Popen) -> None:
        self.process = process

    def startForward(self) -> None:
        if self.isForwarding():
            raise RuntimeError("Forwarder is already forwarding")

        command_list = [
            "/bin/socat",
            f"TCP-LISTEN:{self.server_origin_port},fork",
            f"{self.container_ip}:{self.container_destination_port}",
        ]
        kw_args = {"stdin": DEVNULL, "stdout": DEVNULL, "stderr": DEVNULL}

        self.process = Popen(command_list, **kw_args, shell=False)

    def stopForward(self) -> None:
        if not self.isForwarding():
            raise RuntimeError("Forwarder is not forwarding")

        self.process.terminate()


class PortForwardingInterface:
    def __init__(
        self, forwardable_port_range: range | list = DEFAULT_FORWARDABLE_PORT_RANGE
    ):
        self.available_port_list = list(forwardable_port_range)
        self.stored_forwarders_instance_dict = {}

    def getStoredForwarder(self, container_ip: str) -> None | ForwarderInstance:
        return self.stored_forwarders_instance_dict.get(container_ip)

    def listStoredForwarders(self) -> list:
        return self.forwarding_rule_instance_list.keys()

    def storeForwarder(self, forwarder_instance: ForwarderInstance) -> None:
        if forwarder_instance.getContainerIP() in self.listStoredForwarders():
            raise ValueError("A forwarder already exists for this container IP")

        self.forwarding_rule_instance_list.update(
            {forwarder_instance.getContainerIP(): forwarder_instance}
        )
        self.available_port_list.remove(forwarder_instance.getServerOriginPort())

    def createForwarder(
        self,
        container_ip: str,
        container_destination_port: int,
        store: bool = DEFAULT_STORE_FORWARDER,
    ) -> ForwarderInstance:
        if not len(self.available_port_list):
            raise RuntimeError("All available ports are busy")

        new_server_origin_port = None

        while True:
            new_server_origin_port = random.choice(self.available_port_list)

            if isPortBindable(new_server_origin_port):
                break

            time.sleep(1)

        new_forwarder_instance = ForwarderInstance(
            random.choice(self.available_port_list),
            container_ip,
            container_destination_port,
        )

        if store:
            self.storeForwarder(new_forwarder_instance)

        return new_forwarder_instance

    def deleteStoredForwarder(
        self, container_ip: str, stop_forward: bool = DEFAULT_STOP_FORWARD
    ) -> None:
        forwarder_instance = self.getStoredForwarder(container_ip)

        if stop_forward:
            if forwarder_instance and forwarder_instance.isForwarding():
                forwarder_instance.stopForward()

        self.stored_forwarders_instance_dict.pop(container_ip, None)

        if forwarder_instance:
            self.available_port_list.append(forwarder_instance.getServerOriginPort())
