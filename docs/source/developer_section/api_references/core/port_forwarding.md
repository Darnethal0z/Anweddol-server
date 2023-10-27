# Port forwarding

---

## class *ForwarderInstance*

Constant name                    | Value                     | Definition
-------------------------------- | ------------------------- | ----------
*DEFAULT_STORE_FORWARDER*        | `True`                    | Store the forwarder once created or not.
*DEFAULT_STOP_FORWARD*           | `False`                   | Stop the forwarder if running or not.
*DEFAULT_FORWARDABLE_PORT_RANGE* | `range(10000, 15000)`     | The default AES key size.

### Definition

```{class} anwdlserver.core.port_forwarding.ForwarderInstance(server_origin_port, container_ip, container_uuid, container_destination_port)
```

This class provides the Anweddol server with port forwarding features. It is used to allow clients and container domains to communicate.

**Parameters** :

> ```{attribute} server_origin_port
> Type : int
> 
> The server port to bind to the forwarder.
> ```

> ```{attribute} container_ip
> Type : int
> 
> The destination container IP to forward packets to.
> ```

> ```{attribute} container_uuid
> Type : int
> 
> The destination container UUID.
> ```

> ```{attribute} container_destination_port
> Type : int
> 
> The container destination port to forward packets to.
> ```

```{note} 
The parameter `container_uuid` is used for management fins only.
```

```{note}
The forwarder will be automatically stopped with the `stopForward()` method on the `__del__` method. The `server_origin_port` will be bind to a `socat` object, forwarding any input packets from this port to `container_ip`:`container_destination_port`.
```

### General usage

```{classmethod} isForwarding()
```

Check if the forwarder is forwarding.

**Parameters** : 

> None.

**Return value** : 

> Type : bool
>
> `True` if the forwarder is forwarding, `False` otherwise.

---

```{classmethod} getServerOriginPort()
```

Get the server origin port.

**Parameters** : 

> None.

**Return value** : 

> Type : int
>
> The server origin port.

---

```{classmethod} getContainerIP()
```

Get the destination container IP.

**Parameters** : 

> None.

**Return value** : 

> Type : str
>
> The destination container IP.

---

```{classmethod} getContainerUUID()
```

Get the destination container UUID.

**Parameters** : 

> None.

**Return value** : 

> Type : str
>
> The destination container UUID.

---

```{classmethod} getContainerDestinationPort()
```

Get the container destination port.

**Parameters** : 

> None.

**Return value** : 

> Type : int
>
> The container destination port.

---

```{classmethod} getProcess()
```

Get the forwarder `subprocess.Popen` process object.

**Parameters** : 

> None.

**Return value** : 

> Type : `subprocess.Popen`
>
> The forwarder `subprocess.Popen` process object.

---

```{classmethod} setServerOriginPort(server_origin_port)
```

Set the server port to bind to the forwarder.

**Parameters** : 

> ```{attribute} server_origin_port
> Type : int
> 
> The server origin port to set.
> ```

**Return value** : 

> `None`.

---

```{classmethod} setContainerIP(container_ip)
```

Set the destination container IP to forward packets to.

**Parameters** : 

> ```{attribute} container_ip
> Type : str
> 
> The destination container IP to set.
> ```

**Return value** : 

> `None`.

---

```{classmethod} setContainerDestinationPort(container_destination_port)
```

Set the container destination port.

**Parameters** : 

> ```{attribute} container_destination_port
> Type : int
> 
> The container destination port to forward packets to.
> ```

**Return value** : 

> `None`.

---

```{classmethod} setProcess(process)
```

Set the forwarder `subprocess.Popen` process object.

**Parameters** : 

> ```{attribute} process
> Type : `subprocess.Popen`
> 
> The forwarder `subprocess.Popen` process object to set.
> ```

**Return value** : 

> `None`.

### Forwarder process lifecycle control

```{classmethod} startForward()
```

Start the forwarding process.

**Parameters** : 

> None.

**Return value** : 

> `None`.

**Possible raise classes** : 

> ```{exception} RuntimeError
> An error occured due to a failed internal action.
>
> Raised in this method if the forwarding process is already started.
> ```

---

```{classmethod} stopForward()
```

Stop the forwarding process.

**Parameters** : 

> None.

**Return value** : 

> `None`.

**Possible raise classes** : 

> ```{exception} RuntimeError
> An error occured due to a failed internal action.
>
> Raised in this method if the forwarding process is not started.
> ```

## class *PortForwardingInterface*

### Definition

```{class} anwdlserver.core.port_forwarding.PortForwardingInterface(forwardable_port_range)
```

Provides `ForwarderInstance` management features.

**Parameters** : 

> ```{attribute} forwardable_port_range
> Type : range | list
> 
> The port range / list in which forwarders will be assigned. Default is `range(10000, 15000)`.
> ```

### General usage

```{classmethod} getStoredForwarder(container_uuid)
```

Get a stored forwarder.

**Parameters** : 

> ```{attribute} container_uuid
> Type : str
> 
> The forwarder destination container UUID to get.
> ```

**Return value** : 

> Type : `ForwarderInstance`
>
> The `ForwarderInstance` object of the stored forwarder if exists, `None` otherwise.

---

```{classmethod} listStoredForwarders()
```

List stored forwarders.

**Parameters** : 

> None.

**Return value** : 

> Type : list
>
> A list containing the stored forwarder destination container IPs as strings.

### Forwarder management

```{classmethod} storeForwarder(forwarder_instance)
```

Store a forwarder.

**Parameters** : 

> ```{attribute} forwarder_instance
> Type : `ForwarderInstance`
> 
> The `ForwarderInstance` object to store.
> ```

**Return value** : 

> `None`.

**Possible raise classes** : 

> ```{exception} ValueError
> An error occured due to an invalid value set before or during the method call.
> 
> Raised in this method if the specified forwarder already exists on storage.
> ```

---

```{classmethod} createForwarder(container_ip, container_uuid, container_destination_port, store)
```

Create a forwarder.

**Parameters** : 

> ```{attribute} container_ip
> Type : str
> 
> The destination container IP.
> ```

> ```{attribute} container_uuid
> Type : str
> 
> The destination container UUID.
> ```

> ```{attribute} container_destination_port
> Type : int
> 
> The container destination port.
> ```

> ```{attribute} store
> Type : bool
> 
> `True` to store the created forwarder, `False` otherwise. Default is `True`.
> ```

**Return value** : 

> Type : `ForwarderInstance` 
> 
> The `ForwarderInstance` object of the created forwarder.

```{note} 
The parameter `container_uuid` is used for management fins only.
```

---

```{classmethod} deleteStoredForwarder(container_uuid, stop_forward)
```

Delete a stored forwarder.

**Parameters** : 

> ```{attribute} container_uuid
> Type : str
> 
> The forwarder destination container UUID.
> ```

> ```{attribute} stop_forward
> Type : bool
> 
> `True` to stop the forwarder process before deletion, `False` otherwise. Default is `False`.
> ```

**Return value** : 

> `None`.