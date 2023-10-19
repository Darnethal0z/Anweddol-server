# Utilities

---

## System verification utilities

### Check if a port is bindable

```{function} anwdlserver.core.utilities.isPortBindable(port)
```

Check if a port is bindable.

**Parameters** :

> ```{attribute} port
> Type : int
> 
> The port whose bindability must be checked. It must be an integer between `1` and `65535`.
> ```

**Return value** : 

> Type : bool
>
> `True` if the port is bindable, `False` otherwise.

### Check is a network interface exists on system

```{function} anwdlserver.core.utilities.isInterfaceExists(interface_name)
```

Check if the network interface exists on the system.

**Parameters** :

> ```{attribute} interface_name
> Type : str
> 
> The interface name whose existence must be checked.
> ```

**Return value** : 

> Type : bool
>
> `True` if the interface exists, `False` otherwise.

### Check if a user exists on system

```{function} anwdlserver.core.utilities.isUserExists(username)
```

Check if the username exists on the system.

**Parameters** :

> ```{attribute} username
> Type : str
> 
> The username whose existence must be checked.
> ```

**Return value** : 

> TYpe : bool
>
> `True` if the username exists, `False` otherwise.

### Check if a socket is closed

```{function} anwdlserver.core.utilities.isSocketClosed(socket_descriptor)
```

Check if a socket descriptor is closed.

**Parameters** :

> ```{attribute} socket_descriptor
> Type : `socket.socket`
> 
> The socket descriptor to check.
> ```

**Return value** : 

> Type : bool
>
> `True` if the socket descriptor is closed, `False` otherwise.

## Format verification utilities

### Check if an IP is a valid IPv4 format

```{function} anwdlserver.core.utilities.isValidIP(ip)
```

Check if the IP is a valid IPv4 format.

**Parameters** :

> ```{attribute} ip
> Type : str
> 
> The IP to check as a string.
> ```

**Return value** : 

> Type : bool
>
> `True` if the IP is valid , `False` otherwise.

