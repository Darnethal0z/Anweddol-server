# Utilities

---

> Miscellaneous features

> Package `anwdlserver.core.util`

## Constants

None

## Functions

```
isPortBindable(port: int) -> bool
```

> Check if a port is bindable

_Parameters_ :

- `port` : The port to check. It must be an integer between 1 and 65535

_Return value_ :

- `True` if the port is bindable, `False` otherwise

---

```
isSocketClosed(socket_descriptor: socket.socket) -> bool
```

> Check if a socket descriptor is closed

_Parameters_ :

- `socket_descriptor` : The socket descriptor to check

_Return value_ :

- `True` if the socket descriptor is closed, `False` otherwise

---

```
isValidIP(ip: str) -> bool
```

> Check if the IP is a valid IPv4 format

_Parameters_ :

- `ip` : The IP to check as a string

_Return value_ :

- `True` if the IP is valid , `False` otherwise

---

```
isInterfaceExists(interface_name: str) -> bool
```

> Check if the network interface exists on the system

_Parameters_ :

- `interface_name` : The interface name to check as a string

_Return value_ :

- `True` if the interface exists , `False` otherwise
