# Virtualization

---

## class *VirtualizationInterface*

### Definition

```{class} anwdlserver.core.virtualization.VirtualizationInterface()
```

Provides `ContainerInstance` management features.

**Parameters** : 

> None.

### General usage

```{classmethod} getStoredContainersAmount()
```

Get the stored containers amount.

**Parameters** : 

> None.

**Return value** : 

> The amount of stored containers amount on the instance.

---

```{classmethod} listStoredContainers()
```

List stored containers.

**Parameters** : 

> None.

**Return value** : 

> A list containing the stored container UUIDs as strings.

### Containers management

```{classmethod} createContainer(iso_path: str, store: bool) -> ContainerInstance
```

Create a container.

**Parameters** :

> ```{attribute} iso_path
> > Type : str
> 
> The ISO file path that will be used for the container domain.
> ```

> ```{attribute} store
> > Type : bool
> 
> `True` to store the created container instance, `False` otherwise. Default is `True`.
> ```

**Return value** : 

> The `ContainerInstance` object of the created container.

---

```{classmethod} getStoredContainer(container_uuid)
```

Get a stored container.

**Parameters** :

> ```{attribute} container_uuid
> > Type : str
> 
> The container [UUID](../../../technical_specifications/core/client_authentication.md) to search for.
> ```

**Return value** : 

> The `ContainerInstance` object of the stored container if exists, `None` otherwise.

---

```{classmethod} addStoredContainer(container_instance)
```

Add a container on storage.

**Parameters** :

> ```{attribute} container_instance
> > Type : `ContainerInstance`
> 
> The `ContainerInstance` object to store.
> ```

**Return value** : 

> `None`.

**Possible raise classes** : 

> ```{exception} ValueError
> An error occured due to an invalid value set before or during the method call.
> 
> Raised in this method if the specified container instance already exists on storage.
> ```

---

```{classmethod} deleteStoredContainer(container_uuid)
```

Delete a stored container.

**Parameters** :

> ```{attribute} container_uuid
> > Type : str
> 
> The [UUID](../../../technical_specifications/core/client_authentication.md) of the container to delete.
> ```

**Return value** : 

> `None`.

## class *ContainerInstance*

### Definition

```{class} anwdlserver.core.virtualization.ContainerInstance(iso_path, container_uuid, memory, vcpus, nat_interface_name)
```

Represents a container instance.

**Parameters** :

> ```{attribute} iso_path
> > Type : str
> 
> The ISO file path that will be used for the container domain.
> ```

> ```{attribute} container_uuid
> > Type : str
> 
> The new [container UUID](../../../technical_specifications/core/client_authentication.md). Default is `None`.
> ```

> ```{attribute} memory
> > Type : int
> 
> The memory amount to set on the container domain, exprimed in Mb. Default is `2048`.
> ```

> ```{attribute} vcpus
> > Type : int
> 
> The Virtual CPUs amount to set on the container domain. Default is `2`.
> ```

> ```{attribute} nat_interface_name
> > Type : str
> 
> The [NAT interface name](../../../technical_specifications/core/networking.md) that will be used by the container domain. Default is `virbr0`.
> ```

```{note}
If used, the parameter `iso_path` is already taken care by the `ServerInterface()` class in order to facilitate its usage.
```

### General usage

```{classmethod} isDomainRunning()
```

Check if the container domain is running.

**Parameters** : 

> None.

**Return value** : 

> `True` if the domain is running, `False` otherwise.

---

```{classmethod} getNATInterfaceName()
```

Get the NAT interface name of the instance.

**Parameters** : 

> None.

**Return value** : 

> The NAT interface name of the instance.

---

```{classmethod} getDomainDescriptor()
```

Get the `libvirt.virDomain` object of the instance.

**Parameters** : 

> None.

**Return value** : 

> The `libvirt.virDomain` object of the instance, or `None` is unavailable.

---

```{classmethod} getUUID()
```

Get the instance [container UUID](../../../technical_specifications/core/client_authentication.md).

**Parameters** : 

> None.

**Return value** : 

> The [container UUID](../../../technical_specifications/core/client_authentication.md) of the instance.

---

```{classmethod} getISOFilePath()
```

Get the instance ISO file path.

**Parameters** : 

> None.

**Return value** : 

> The instance ISO file path on local storage.

---

```{classmethod} getMAC()
```

Get the container domain MAC address.

**Parameters** : 

> None.

**Return value** : 

> The instance container domain MAC address, or `None` if unavailable.

**Possible raise classes** :

> ```{exception} RuntimeError
> An error occured due to a failed internal action.
> 
> Raised in this method if the container domain is not created.
> ```

---

```{classmethod} getIP()
```

Get the container domain IP address.

**Parameters** : 

> None.

**Return value** : 

> The container domain IP address, or `None` if the domain is not started or not ready yet.

**Possible raise classes** :

> ```{exception} RuntimeError
> An error occured due to a failed internal action.
> 
> Raised in this method if the container domain is not created.
> ```

```{warning}
The container domain must be started and ready in order to get its IP, since the method will fetch it from the dnsmasq interface status file located in `/var/lib/libvirt/dnsmasq/` with its MAC address.
```

---

```{classmethod} getMemory()
```

Get the allocated container domain memory amount.

**Parameters** : 

> None.

**Return value** : 

> The memory amount allocated to the container domain, exprimed in Mb.

---

```{classmethod} getVCPUs()
```

Get the allocated container domain virtual CPUs amount.

**Parameters** : 

> None.

**Return value** : 

> The virtual CPUs amount allocated to the container domain.

---

```{classmethod} setDomainDescriptor(domain_descriptor)
```

Set the `libvirt.virDomain` object.

**Parameters** :

> ```{attribute} domain_descriptor
> > Type : `libvirt.virDomain`
> 
> The `libvirt.virDomain` object to set on the instance.
> ```

**Return value** : 

> `None`.

---

```{classmethod} makeISOFileChecksum()
```

Make the SHA256 digest of the container ISO file.

**Parameters** : 

> None.

**Return value** : 

> The SHA256 digest of the container ISO file.

**Possible raise classes** : 

> ```{exception} RuntimeError
> An error occured due to a failed internal action.
> 
> Raised in this method if the ISO file path is not set.
> ```

### Container domain capacity setup

```{classmethod} setISOFilePath(iso_path)
```

Set the container ISO file path.

**Parameters** :

> ```{attribute} iso_path
> > Type : str
> 
> The ISO file path to set.
> ```

**Return value** : 

> `None`.

---

```{classmethod} setMemory(memory)
```

Set the memory amount to allocate on the container domain.

**Parameters** :

> ```{attribute} memory
> > Type : int
> 
> The memory to set, exprimed in Mb. Must be a non-zero value, minimum should be `512`.
> ```

**Return value** : 

> `None`.

---

```{classmethod} setVCPUs(vcpus)
```

Set the virtual CPUs amount to allocate on the container domain.

**Parameters** :

> ```{attribute} memory
> > Type : int
> 
> The amount of virtual CPUs to set. Must be a non-zero value, minimum allowed is `1`.
> ```

**Return value** : 

> `None`.

---

```{classmethod} setNATInterfaceName(nat_interface_name: str) -> None
```

Set the NAT interface name that will be used on the container domain.

**Parameters** :

> ```{attribute} nat_interface_name
> > Type : str
> 
> The NAT interface name that will be used on the container domain.
> ```

**Return value** : 

> `None`.

### Container domain administration

```{classmethod} createEndpointShell(endpoint_username, endpoint_password, endpoint_listen_port, open_shell)
```

Create an `EndpointShell` instance on the container domain.

**Parameters** :

> ```{attribute} endpoint_username
> > Type : str
> 
> The endpoint SSH username to set on the instance. Default is `endpoint`.
> ```

> ```{attribute} endpoint_password
> > Type : str
> 
> The endpoint SSH password to set on the instance. Default is `endpoint`.
> ```

> ```{attribute} endpoint_listen_port
> > Type : int
> 
> The endpoint SSH listen port to set on the instance. Default is `22`.
> ```

> ```{attribute} open_shell
> > Type : bool
> 
> `True` to open the shell on the container instance on initialization, `False` otherwise. Default is `True`.
> ```

**Return value** : 

> The `EndpointShellInstance` object representing the created endpoint shell instance.

### Container domain lifetime control

```{classmethod} startDomain(wait_available: bool, wait_max_tryout: int, driver_uri: str) -> None
```

Start the [container domain](../../../technical_specifications/core/virtualization.md).

**Parameters** :

> ```{attribute} wait_available
> > Type : bool
> 
> `True` to wait for the network to be available on the domain or not. Default is `True`.
> ```

> ```{attribute} wait_max_tryout
> > Type : int
> 
> The amount of attemps to check if the network is available on the domain before raising `TimeoutError`. Default is `20`.
> ```

> ```{attribute} driver_uri
> > Type : str
> 
> The hypervisor [driver URI](https://libvirt.org/uri.html) to use. Default is `qemu:///system`.
> ```

**Return value** : 

> `None`.

**Possible raise classes** :

> ```{exception} TimeoutError
> An error occured due to a timed-out operation on system level.
> 
> Raised in this method if the parameter `wait_available` is set to `True` and that the container domain network is not available after `wait_max_tryout` attemps.
> ```

> ```{exception} RuntimeError
> An error occured due to a failed internal action.
>
> Raised in this method if the container domain is already running.
> ```

---

```{classmethod} stopDomain(destroy)
```

Stop the container domain.

**Parameters** :

> ```{attribute} destroy
> > Type : bool
> 
> Destroy the container domain rather than shutting it down or not. Default is `True`.
> ```

**Return value** : 

> `None`.

**Possible raise classes** :

> ```{exception} RuntimeError
> An error occured due to a failed internal action.
>
> Raised in this method if the container domain is not running.
> ```

## class *EndpointShellInstance*

### Definition

```{class} anwdlserver.core.virtualization.EndpointShellInstance(container_ip, endpoint_username, endpoint_password, endpoint_listen_port, open_shell)
```

Represents a opened SSH shell to a container endpoint.

```{tip}
This class can be used in a 'with' statement.
```

**Parameters** :

> ```{attribute} container_ip
> > Type : str
> 
> The remote container domain IP to connect via SSH to. Default is `None`.
> ```

> ```{attribute} endpoint_username
> > Type : str
> 
> The [endpoint username](../../../technical_specifications/core/virtualization.md) that will be used for container domain administration. Default is `endpoint`.
> ```

> ```{attribute} endpoint_password
> > Type : str
> 
> The [endpoint password](../../../technical_specifications/core/virtualization.md) that will be used for container domain administration. Default is `endpoint`.
> ```

> ```{attribute} endpoint_listen_port
> > Type : int
> 
> The [endpoint listen port](../../../technical_specifications/core/virtualization.md) that will be used for container domain administration. Default is `22`.
> ```

> ```{attribute} open_shell
> > Type : bool
> 
> `True` to open the shell on the container instance on initialization, `False` otherwise. Default is `True`.
> ```

```{note}
The endpoint SSH shell will be clowed with the `closeShell()` method on the `__del__` method.
```

```{warning}
If the parameter `open_shell` is set to `True` and no value is passed on the parameter `container_ip`, no connection will be made on initialization.
```

### General usage

```{classmethod} isClosed()
```

Check if the connection is closed.

**Parameters** : 

> None.

**Return value** : 

> `True` if the connection is closed, `False` otherwise.

---

```{classmethod} getSSHClient()
```

Get the [`paramiko.client.SSHClient`](https://docs.paramiko.org/en/stable/api/client.html) connection object.

**Parameters** : 

> None.

**Return value** : 

> The [`paramiko.client.SSHClient`](https://docs.paramiko.org/en/stable/api/client.html) object of the instance.

---

```{classmethod} getContainerIP()
```

Get the remote container domain IP.

**Parameters** : 

> None.

**Return value** : 

> The remote container domain IP.

---

```{classmethod} getEndpointCredentials()
```

Get the endpoint credentials.

**Parameters** : 

> None.

**Return value** : 

> A tuple representing the endpoint credentials of the instance :

> ```
> {
>   endpoint_username,
>   endpoint_password,
>   endpoint_listen_port
> }
> ``` 

> - *endpoint_username* (Type : str)
> 
>   The endpoint SSH username
> 
> - *endpoint_password* (Type : str)
> 
>   The endpoint SSH password
> 
> - *endpoint_listen_port* (Type : int)
> 
>   The endpoint SSH listen port

---

```{classmethod} getStoredClientSSHCredentials()
```

Get the stored client SSH client credentials.

**Parameters** : 

> None.

**Return value** : 

> A tuple representing the stored client SSH credentials : 

> ```
> (
>   username,
>   password,
>   listen_port
> )
> ```

> - *username* (Type : int)
> 
>   The client SSH username.
> 
> - *password* (Type : int)
> 
>   The client SSH password.
> 
> - *listen_port* (Type : int)
> 
>   The client SSH server listen port.

> Or `None` if the credentials are not set.

---

```{classmethod} setContainerIP(ip)
```

Set the remote container domain IP.

**Parameters** : 

> ```{attribute} ip
> > Type : str
> 
> The remote container domain IP to set.
> ```

**Return value** : 

> `None`.

---

```{classmethod} setEndpointCredentials(username, password, listen_port)
```

Set the remote container domain endpoint SSH credentials.

**Parameters** : 

> ```{attribute} username
> > Type : str
> 
> The endpoint SSH username to set.
> ```

> ```{attribute} password
> > Type : str
> 
> The endpoint SSH password to set.
> ```

> ```{attribute} listen_port
> > Type : str
> 
> The endpoint SSH listen port to set.
> ```

**Return value** : 

> `None`.

---

```{classmethod} storeClientSSHCredentials(client_ssh_username, client_ssh_password)
```

Set the stored client SSH client credentials.

**Parameters** :

> ```{attribute} client_ssh_username
> > Type : str
> 
> The client SSH username to store.
> ```

> ```{attribute} client_ssh_password
> > Type : str
> 
> The client SSH password to store.
> ```

**Return value** : 

> `None`.

```{warning}
In a server context provided with `ServerInterface()`, if you want to set custom client SSH credentials with custom commands executed with the `executeCommand()` method, you must call this method to store those credentials before returning to the server process (see the [Server API page](server.md), events section).
```

---

```{classmethod} openShell()
```

Open an SSH shell on the remote container domain.

**Parameters** : 

> None.

**Return value** : 

> `None`.

**Possible raise classes** : 

> ```{exception} RuntimeError
> An error occured due to a failed internal action.
> 
> Raised in this method if the shell is already opened on the remote container domain.
> ```

---

```{classmethod} generateClientSSHCredentials(password_length, store)
```

Generate new client SSH credentials.

**Parameters** :

> ```{attribute} password_length
> > Type : int
> 
> The password length. Default is `120`.
> ```

> ```{attribute} store
> > Type : bool
> 
> `True` to store the generated credentials on the instance, `False` otherwise.
> ```

**Return value** : 

> A tuple representing the generated client SSH credentials :

> ```
> (
>   username,
>   password
> )
> ```

> - *username* (Type : str)
> 
>   The client SSH username.
> 
> - *password* (Type : str)
> 
>   The client SSH password.

---

```{classmathod} closeShell()
```

Close the SSH connection.

**Parameters** : 

> None.

**Return value** : 

> `None`.

```{note}
**Additional note** : This method is automatically called within the `__del__` method and the `setContainerSSHCredentials` method when called.
```

### Container domain SSH administration

```{classmethod} executeCommand(command)
```

Execute a command on the remote container domain.

**Parameters** :

> ```{attribute} command
> > Type : str
> 
> The BASH command to execute on the container domain.
> ```

**Return value** : 

> A tuple representing the stdout and the stderr of the command output :

> ```
> (
>   stdout,
>   stderr
> )
> ```

> - `stdout` (Type : str)
> 
>   The standard output stream of the result.
> 
> - `stderr` (Type : str)
> 
>   The standard error stream of the result.

---

```{classmethod} administrateContainer()
```

Set the container SSH client credentials on the remote container.

**Parameters** :

> None.

**Return value** : 

> `None`.

**Possible raise classes** :

> ```{exception} RuntimeError
> An error occured due to a failed internal action.
> 
> Raised in this method if the endpoint credentials was not set or the shell is not opened on the remote container domain, or that the method failed to set client SSH credentials on the remote container domain.
> ```

```{note}
This method uses the `anweddol_container_setup.sh` script on the container to set the stored SSH credentials.
```