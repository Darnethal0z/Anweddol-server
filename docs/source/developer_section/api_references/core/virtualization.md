# Virtualization

---

> Virtualization management and utilities, using libvirt API

> Package `anwdlserver.core.virtualization`

## Constants

Default parameters :

| Name                                     | Value                 | Description                                                                              |
| ---------------------------------------- | --------------------- | ---------------------------------------------------------------------------------------- |
| `DEFAULT_LIBVIRT_DRIVER_URI`             | `"qemu:///system"`    | The default server bind address                                                          |
| `DEFAULT_CONTAINER_ENDPOINT_USERNAME`    | `"endpoint"`          | The default server listen port                                                           |
| `DEFAULT_CONTAINER_ENDPOINT_PASSWORD`    | `"endpoint"`          | The default timeout applied on a new client                                              |
| `DEFAULT_CONTAINER_ENDPOINT_LISTEN_PORT` | `22`                  | Start the server asynchronously by default                                               |
| `DEFAULT_BRIDGE_INTERFACE_NAME`          | `"anwdlbr0"`          | The default bridge interface name that container domains will use                        |
| `DEFAULT_NAT_INTERFACE_NAME`             | `"virbr0"`            | The default NAT interface name that container domains will use                           |
| `DEFAULT_CONTAINER_MAX_TRYOUT`           | `20`                  | The maximum attemps to check the network availability of a container domain before error |
| `DEFAULT_MAX_ALLOWED_CONTAINERS`         | `6`                   | The maximum allowed amount of active containers on an instance                           |
| `DEFAULT_CONTAINER_MEMORY`               | `2048`                | The memory, in Mb, allocated to container domains                                        |
| `DEFAULT_CONTAINER_VCPUS`                | `2`                   | The amount of VCPUs allocated to container domains                                       |
| `DEFAULT_CONTAINER_PORT_RANGE`           | `range(10000, 15000)` | The port range that will be assigned to container domains SSH servers                    |
| `DEFAULT_CONTAINER_WAIT_AVAILABLE`       | `True`                | Wait for the network to be available on a container domain before continuing by default  |
| `DEFAULT_CONTAINER_DESTROY_DOMAIN`       | `True`                | Destroy the domain rather than shutting it down by default                               |
| `DEFAULT_STORE_CONTAINER`                | `True`                | Store the container instance on the virtualization interface or not by default           |

## Classes

### `EndpointShellInstance`

#### Definition

```
class EndpointShellInstance(
	ssh_client: paramiko.client.SSHClient
)
```

> Represents a opened SSH shell to a container endpoint

_Parameters_ :

- `ssh_client`: The [`paramiko.client.SSHClient`](https://docs.paramiko.org/en/stable/api/client.html) instance representing the SSH connection.

**NOTE** : The endpoint SSH shell will be automatically closed on `__del__` method.

#### Methods

```
isClosed() -> bool
```

> Check if the connection is closed

_Parameters_ :

- None

_Return value_ :

- A boolean value. `True` if the connection is closed, `False` otherwise

---

```
getSSHClient() -> paramiko.client.SSHClient
```

> Get the [`paramiko.client.SSHClient`](https://docs.paramiko.org/en/stable/api/client.html) connection object

_Parameters_ :

- None

_Return value_ :

- The [`paramiko.client.SSHClient`](https://docs.paramiko.org/en/stable/api/client.html) object of the instance

---

```
getStoredContainerSSHCredentials() -> tuple
```

> Get the stored container SSH credentials

_Parameters_ :

- None

_Return value_ :

- A tuple representing the stored container SSH credentials : 

```
(
	username,
	password,
	listen_port
)
```

- `username` : The SSH username
- `password` : The SSH password
- `listen_port` : The SSH server listen port

**NOTE** : Container SSH credentials are stored on the instance within the `setContainerSSHCredentials` method. For these credentials to be sent to the client in the server process, you need to call this method if you want to set specific credentials.

---

```
executeCommand(command: str) -> tuple
```

> Execute a command on the remote container

_Parameters_ :

- `command` : The command to execute

_Return value_ :

- A tuple representing the stdout and the stderr of the command output :

```
(
	stdout,
	stderr
)
```

- `stdout` : The standard output stream of the result
- `stderr` : The standard error stream of the result

---

```
generateContainerSSHCredentials(
	port_range: range = DEFAULT_CONTAINER_PORT_RANGE,
) -> tuple
```

> Generate new container SSH credentials

_Parameters_ :

- `port_range` : The port range which a random new listen port is chosen

_Return value_ :

- A tuple representing the generated container SSH credentials :

```
(
	username,
	password,
	listen_port
)
```

- `username` : The SSH username
- `password` : The SSH password
- `listen_port` : The SSH server listen port

---

```
setContainerSSHCredentials(
	username: str,
    password: str,
    listen_port: int,
) -> None
```

> Set the container SSH credentials on the remote container

_Parameters_ :

- `username` : The SSH username to set
- `password` : The SSH password to set
- `listen_port` : The SSH server listen port to set

_Return value_ :

- None

**NOTE** : This method uses the `anweddol_container_setup.sh` script on the container to set the SSH credentials on ot, thus calling the `closeShell` method after completion (see the technical specifications [Virtualization section](https://anweddol-server.readthedocs.io/en/latest/technical_specifications/core/virtualization.html#administration)) to learn more).

---

```
closeShell() -> None
```

> Close the SSH connection

_Parameters_ :

- None

_Return value_ :

- None

**NOTE** : This method is automatically called within the `__del__` method and the `setContainerSSHCredentials` method when called, but it is programatically better to call it naturally

### `ContainerInstance`

#### Definition

```
class ContainerInstance(
	uuid: str,
	iso_path: str,
	memory: int = DEFAULT_CONTAINER_MEMORY,
	vcpus: int = DEFAULT_CONTAINER_VCPUS,
	nat_interface_name: str = DEFAULT_NAT_INTERFACE_NAME,
	bridge_interface_name: str = DEFAULT_BRIDGE_INTERFACE_NAME,
	endpoint_username: str = DEFAULT_CONTAINER_ENDPOINT_USERNAME,
	endpoint_password: str = DEFAULT_CONTAINER_ENDPOINT_PASSWORD,
	endpoint_listen_port: int = DEFAULT_CONTAINER_ENDPOINT_LISTEN_PORT
)
```

> Represents a container instance

_Parameters_ :

- `uuid` : The new [container UUID](https://anweddol-server.readthedocs.io/en/latest/technical_specifications/core/client_authentication.html#session-credentials)
- `iso_path` : The ISO path that will be used for the container domain
- `memory` : The memory amount to allocate on the container, exprimed in Mb
- `vcpus` : The VCPUs amount to allocate on the container
- `nat_interface_name` : The [NAT interface name](https://anweddol-server.readthedocs.io/en/latest/technical_specifications/core/networking.html#container) that will be used by the container
- `bridge_interface_name` : [The bridge interface](https://anweddol-server.readthedocs.io/en/latest/technical_specifications/core/networking.html#container) name that will be used by the container
- `endpoint_username` : The [endpoint username](https://anweddol-server.readthedocs.io/en/latest/technical_specifications/core/virtualization.html#administration) that will be used for container administration
- `endpoint_password` : The [endpoint password](https://anweddol-server.readthedocs.io/en/latest/technical_specifications/core/virtualization.html#administration) that will be used for container administration
- `endpoint_listen_port` : The [endpoint listen port](https://anweddol-server.readthedocs.io/en/latest/technical_specifications/core/virtualization.html#administration) that will be used for container administration

#### Methods

```
isDomainRunning() -> bool
```

> Check if the container domain is running

_Parameters_ :

- None

_Return value_ :

- A boolean value. `True` if the domain is running, `False` otherwise

---

```
getNATInterfaceName() -> str
```

> Get the NAT interface name of the instance

_Parameters_ :

- None

_Return value_ :

- The NAT interface name of the instance

---

```
getBridgeInterfaceName() -> str
```

> Get the bridge interface name of the instance

_Parameters_ :

- None

_Return value_ :

- The bridge interface name of the instance

---

```
getDomainDescriptor() -> None | libvirt.virDomain
```

> Get the `libvirt.virDomain` object of the instance

_Parameters_ :

- None

_Return value_ :

- The `libvirt.virDomain` object of the instance, or `None` is unavailable

---

```
getUUID() -> str
```

> Get the instance [container UUID](https://anweddol-server.readthedocs.io/en/latest/technical_specifications/core/client_authentication.html#session-credentials)

_Parameters_ :

- None

_Return value_ :

- The [container UUID](https://anweddol-server.readthedocs.io/en/latest/technical_specifications/core/client_authentication.html#session-credentials) of the instance

---

```
getISOPath() -> str
```

> Get the instance ISO path

_Parameters_ :

- None

_Return value_ :

- The instance ISO path on local storage

---

```
getMAC() -> str
```

> Get the container MAC address

_Parameters_ :

- None

_Return value_ :

- The instance container MAC address

_Possible raise classes_ :

- `RuntimeError`

**NOTE** : The container domain must be started and ready in order to get its MAC address.

---

```
getIP() -> None | str
```

> Get the container IP address

_Parameters_ :

- None

_Return value_ :

- The instance container IP address, or `None` if the domain is not started or not ready yet

_Possible raise classes_ :

- `RuntimeError`

**NOTE** : The container domain must be started and ready in order to get its IP, since the method will fetch it from the dnsmasq interface status file located in `/var/lib/libvirt/dnsmasq/` with its MAC address.

---

```
getMemory() -> int
```

> Get the allocated container memory amount

_Parameters_ :

- None

_Return value_ :

- The memory amount allocated to the container

---

```
getVCPUs() -> int
```

> Get the allocated container Virtual CPUs amount

_Parameters_ :

- None

_Return value_ :

- The VCPUs amount allocated to the container 

---

```
setDomainDescriptor(domain_descriptor: libvirt.virDomain) -> None
```

> Set the `libvirt.virDomain` object of the instance

_Parameters_ :

- `domain_descriptor` : The `libvirt.virDomain` object to set on the instance

_Return value_ :

- None

---

```
setISOPath(iso_path: str) -> None
```

> Set the container ISO path of the instance

_Parameters_ :

- `iso_path` : The ISO path to set on the instance

_Return value_ :

- None

---

```
setMemory(memory: int) -> None
```

> Set the memory amount to allocate on the container

_Parameters_ :

- `memory` : The memory to allocate on the container, exprimed in Mb

_Return value_ :

- None

**NOTE** : The parameter `memory` must be a value greater than 0

---

```
setVCPUs(vcpus: int) -> None
```

> Set the Virtual CPUs amount to allocate on the container

_Parameters_ :

- `vcpus` : The amount of VCPUs to allocate on the container

_Return value_ :

- None

**NOTE** : The parameter `vcpus` must be a value greater than 0

---

```
setNATInterfaceName(nat_interface_name: str) -> None
```

> Set the NAT interface name of the container

_Parameters_ :

- `nat_interface_name` : The NAT interface name that will be used on the container domain

_Return value_ :

- None

---

```
setBridgeInterfaceName(bridge_interface_name: str) -> None
```

> Set the bridge interface name of the container

_Parameters_ :

- `bridge_interface_name` : The bridge interface name that will be used on the container domain

_Return value_ :

- None

---

```
setEndpointSSHAuthenticationCredentials(
	endpoint_username: str = DEFAULT_CONTAINER_ENDPOINT_USERNAME, 
    endpoint_password: str = DEFAULT_CONTAINER_ENDPOINT_PASSWORD, 
    endpoint_listen_port: str = DEFAULT_CONTAINER_ENDPOINT_LISTEN_PORT
) -> None
```

> Set the container [endpoint SSH credentials](https://anweddol-server.readthedocs.io/en/latest/technical_specifications/core/virtualization.html#administration) for SSH authentication

_Parameters_ :

- `endpoint_username` : The endpoint username to set
- `endpoint_password` : The endpoint password to set
- `endpoint_listen_port` : The endpoint listen port to set

_Return value_ :

- None

---

```
makeISOChecksum() -> str
```

> Get the SHA256 digest of the instance container ISO

_Parameters_ :

- None

_Return value_ :

- The SHA256 digest of the container ISO

---

```
createEndpointShell() -> EndpointShellInstance
```

> Create a `EndpointShellInstance` object on the running container

_Parameters_ :

- None

_Return value_ :

- The `EndpointShellInstance` object representing the SSH shell on the container domain endpoint

---

```
startDomain(
	wait_available: bool = DEFAULT_CONTAINER_WAIT_AVAILABLE,
    wait_max_tryout: int = DEFAULT_CONTAINER_MAX_TRYOUT,
    driver_uri: str = DEFAULT_LIBVIRT_DRIVER_URI
) -> None
```

> Start the [container domain](https://anweddol-server.readthedocs.io/en/latest/technical_specifications/core/virtualization.html#api)

_Parameters_ :

- `wait_available` : Wait for the network to be available on the domain or not
- `wait_max_tryout` : The amount of attemps to check if the network is available on the domain before raising `TimeoutError`
- `driver_uri` : The hypervisor [driver URI](https://libvirt.org/uri.html) to use.

_Return value_ :

- None

_Possible raise classes_ :

- `RuntimeError`
- `TimeoutError`

**NOTE** : By default, the qemu hypervisor URI `qemu:///system` is used. The container domain must be stopped before being started.

---

```
stopDomain(destroy: bool = DEFAULT_CONTAINER_DESTROY_DOMAIN) -> None
```

> Stop the container domain

_Parameters_ :

- `destroy` : Destroy the container domain rather than shutting it down or not

_Return value_ :

- None

_Possible raise classes_ :

- `RuntimeError`

**NOTE** : The container domain must be running before being stopped.

### `VirtualizationInterface`

#### Definition

```
class VirtualizationInterface(
	container_iso_path: str,
    max_allowed_containers: int = DEFAULT_MAX_ALLOWED_CONTAINERS,
)
```

> Provides container management functionality

_Parameters_ :

- `container_iso_path` : The container ISO path to set on created containers
- `max_allowed_containers` : The maximum allowed active containers amount on the instance, must be greater than 0

#### Methods

```
getIsoPath() -> str
```

> Get the instance ISO path

_Parameters_ :

- None

_Return value_ :

- The instance ISO path

---

```
getMaxAllowedContainersAmount() -> int
```

> Get the maximum allowed active containers amount on the instance

_Parameters_ :

- None

_Return value_ :

- The maximum allowed active containers amount on the instance, is greater than 0

---

```
getContainersAmount() -> int
```

> Get the active containers amount on the instance

_Parameters_ :

- None

_Return value_ :

- The amount of active containers on the instance

---

```
getAvailableContainersAmount() -> int
```

> Get the amount of available containers left

_Parameters_ :

- None

_Return value_ :

- The amount of available containers left

**NOTE** : This method justs substract the maximum allowed active containers amount on the instance with the actual active containers amount.

---

```
listStoredContainers() -> list
```

> List stored containers

_Parameters_ :

- None

_Return value_ :

- A list enumerating the stored container UUIDs

---

```
getStoredContainer(container_uuid: str) -> None | ContainerInstance
```

> Get a stored container

_Parameters_ :

- `container_uuid` : The container UUID to search for

_Return value_ :

- The `ContainerInstance` object of the crated container if exists, `None` otherwise

---

```
setIsoPath(iso_path: str) -> None
```

> Set the instance ISO path

_Parameters_ :

- `iso_path` : The instance ISO path to set. Must point to a valid ISO image

_Return value_ :

- None

---

```
setMaxAllowedContainers(max_allowed_containers: int) -> None
```

> Set the maximum allowed active container amount on the instance

_Parameters_ :

- `max_allowed_containers` : The maximum allowed active containers amount on the instance, must be greater than 0

_Return value_ :

- None

---

```
addStoredContainer(container_instance: ContainerInstance) -> None
```

> Add a container on the instance

_Parameters_ :

- `container_instance` : The `ContainerInstance` object to add

_Return value_ :

- None

_Possible raise classes_ : 

- `RuntimeError`

**NOTE** : If the stored container amount become equal to the `max_allowed_containers` value from the class initialization, a `RuntimeError` will be raised.

---

```
deleteStoredContainer(container_uuid: str) -> None
```

> Delete a stored container

_Parameters_ :

- `container_instance` : The [container UUID](https://anweddol-server.readthedocs.io/en/latest/technical_specifications/core/client_authentication.html#session-credentials) to delete

_Return value_ :

- None

---

```
createContainer(store: bool = DEFAULT_STORE_CONTAINER) -> ContainerInstance
```

> Create a container

_Parameters_ :

- `store` : `True` to store the created container, `False` otherwise

_Return value_ :

- The `ContainerInstance` object of the created container

_Possible raise classes_ : 

- `RuntimeError`

**NOTE** : If the stored container amount become equal to the `max_allowed_containers` value from the class initialization, a `RuntimeError` will be raised.