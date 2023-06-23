# Server

---

> Server management features

> Package `anwdlserver.core.server`

## Constants

Default values :

| Name                          | Value   | Description                                 |
| ----------------------------- | ------- | ------------------------------------------- |
| `DEFAULT_SERVER_BIND_ADDRESS` | `""`    | The default server bind address             |
| `DEFAULT_SERVER_LISTEN_PORT`  | `6150`  | The default server listen port              |
| `DEFAULT_CLIENT_TIMEOUT`      | `10`    | The default timeout applied on a new client |
| `DEFAULT_ASYCHRONOUS`         | `False` | Start the server synchronously by default   |

Constants definition :

| Name                           | Value                  | Description                                                             |
| ------------------------------ | ---------------------- | ----------------------------------------------------------------------- |
| `REQUEST_VERB_CREATE`          | `"CREATE"`             | The verb indicating the intent to create a new container                |
| `REQUEST_VERB_DESTROY`         | `"DESTROY"`            | The verb indicating the intent to destroy a container                   |
| `REQUEST_VERB_STAT`            | `"STAT"`               | The verb indicating the intent to get the server runtime statistics     |
| `RESPONSE_MSG_OK`              | `"OK"`                 | Message specifying that the request was correctly handled by the server |
| `RESPONSE_MSG_BAD_AUTH`        | `"Bad authentication"` | Message specifying that invalid credentials were given to the server    |
| `RESPONSE_MSG_BAD_REQ`         | `"Bad request"`        | Message specifying that the received request is malformed               |
| `RESPONSE_MSG_REFUSED_REQ`     | `"Refused request"`    | Message specifying that the received request was refused                |
| `RESPONSE_MSG_UNAVAILABLE`     | `"Unavailable"`        | Message specifying that the server is currently unavailable             |
| `RESPONSE_MSG_INTERNAL_ERROR`  | `"Internal error"`     | Message specifying that the server experienced an internal error        |
| `EVENT_CLIENT`                 | `1`                    | Identifies the `on_client` callback method                              |
| `EVENT_CLIENT_CLOSED`          | `2`                    | Identifies the `on_client_closed` callback method                       |
| `EVENT_CONNECTION`             | `3`                    | Identifies the `on_connection` callback method                          |
| `EVENT_CREATED_CONTAINER`      | `4`                    | Identifies the `on_created_container` callback method                   |
| `EVENT_CREATED_ENDPOINT_SHELL` | `5`                    | Identifies the `on_created_endpoint_shell` callback method              |
| `EVENT_DESTROYED_CONTAINER`    | `6`                    | Identifies the `on_destroyed_container` callback method                 |
| `EVENT_MALFORMED_REQUEST`      | `7`                    | Identifies the `on_malformed_request` callback method                   |
| `EVENT_REQUEST`                | `8`                    | Identifies the `on_request` callback method                             |
| `EVENT_RUNTIME_ERROR`          | `9`                    | Identifies the `on_runtime_error` callback method                       |
| `EVENT_STARTED`                | `10`                   | Identifies the `on_started` callback method                             |
| `EVENT_STOPPED`                | `11`                   | Identifies the `on_stopped` callback method                             |
| `EVENT_UNKNOWN_VERB`           | `12`                   | Identifies the `on_unknown_verb` callback method                        |

## Classes

### `ServerInterface`

#### Definition

```
class ServerInterface(
	container_iso_path: str = None,
	bind_address: str = DEFAULT_SERVER_BIND_ADDRESS,
	listen_port: int = DEFAULT_SERVER_LISTEN_PORT,
	client_timeout: int = DEFAULT_CLIENT_TIMEOUT,
	runtime_virtualization_interface: VirtualizationInterface = None,
	runtime_database_interface: DatabaseInterface = None,
	runtime_rsa_wrapper: RSAWrapper = None
)
```

> Main server utility class

_Parameters_ :

- `container_iso_path` : The container ISO path that will be used for containers
- `bind_address` : The bind address that the server will be using
- `listen_port` : The listen port that the server will be using
- `client_timeout` : The timeout that will be applied to clients
- `runtime_virtualization_interface` : The `VirtualizationInterface` instance that will be used by the server
- `runtime_database_interface` : The `DatabaseInterface` instance that will be used by the server
- `runtime_rsa_wrapper` : The `RSAWrapper` instance that will be used by the server

**NOTE** : The container ISO path must point to a valid [ISO image](https://anweddol-server.readthedocs.io/en/latest/administration_guide/container_iso.html). The server is automatically stopped when the `__del__` method is called.

#### Methods

```
getRuntimeDatabaseInterface() -> DatabaseInterface
```

> Returns the runtime `DatabaseInterface` instance

_Parameters_ :

- None

_Return value_ :

- The `DatabaseInterface` instance used by the server

---

```
getRuntimeVirtualizationInterface() -> VirtualizationInterface
```

> Returns the runtime `VirtualizationInterface` instance

_Parameters_ :

- None

_Return value_ :

- The `VirtualizationInterface` instance used by the server

---

```
getRuntimeRSAWrapper() -> RSAWrapper
```

> Returns the runtime `RSAWrapper` instance

_Parameters_ :

- None

_Return value_ :

- The `RSAWrapper` instance used by the server

---

```
getRuntimeStatistics() -> tuple
```

> Returns the server's actual runtime statistics

_Parameters_ :

- None

_Return value_:

- A tuple containing the server runtime statistics :

```
(
	is_running,
	recorded_runtime_errors_amount,
	uptime,
	available_containers_amount
)
```

- `is_running` : Boolean value set to `True` if the server is currently running, `False` otherwise
- `recorded_runtime_errors_amount` : The amount of errors recorded during the runtime
- `uptime` : The server uptime, exprimed in seconds
- `available_containers_amount` : The available containers amount

---

```
setRequestHandler(verb: str, routine: callable) -> None
```

> Set a request handler

_Parameters_ :

- `verb` : The request verb to handle. It can be a custom one or a normalized one :
  - `REQUEST_VERB_CREATE`
  - `REQUEST_VERB_STAT`
  - `REQUEST_VERB_DESTROY`
- `routine` : A callable object that will be called when a received request verb is equal to `verb` value

_Return value_ :

- None

---

```
setEventHandler(event: int, routine: callable) -> None
```

> Set an event handler

_Parameters_ :

- `event` : The event to handle. It can be :

  - `EVENT_MALFORMED_REQUEST`
  - `EVENT_UNKNOWN_VERB`
  - `EVENT_RUNTIME_ERROR`
  - `EVENT_REQUEST`
  - `EVENT_CONNECTION`
  - `EVENT_CREATED_CONTAINER`
  - `EVENT_CREATED_ENDPOINT_SHELL`
  - `EVENT_CLIENT`
  - `EVENT_STARTED`
  - `EVENT_STOPPED`
  - `EVENT_CLIENT_CLOSED`
  - `EVENT_DESTROYED_CONTAINER`

- `routine` : A callable object that will be called when the `event` event is triggered.

**NOTE** : This is the alternative of callback event decorators. Refer to the [Callback events](https://anweddol-server.readthedocs.io/en/latest/developer_section/api_references/core/server.html#callback-events) section below to know their roles and effects.

---

```
startServer(asynchronous: bool = DEFAULT_ASYCHRONOUS) -> None
```

> Start the server

_Parameters_ :

- `asynchronous` : Start the server asynchronously. Default is `False`, executing it synchronously

_Return value_ :

- None

**NOTE** : The execution is blocked when set to synchronous mode (by default)

---

```
stopServer() -> None
```

> Stop the server

_Parameters_ :

- None

_Return value_:

- None

**NOTE** : This method is automatically called within the `__del__` method, but it is programatically better to call it naturally

---

```
restartServer(asynchronous: bool = DEFAULT_ASYCHRONOUS) -> None
```

> Restart the server

_Parameters_ :

- `asynchronous` : Start the server asynchronously. Default is `False`, executing it synchronously

_Return value_ :

- None

#### Callback events

Callback events are decorators used to bind a routine or a callable object to an intern event.

```
# The decorator depicting the event. Here EVENT_CREATED_CONTAINER
@ServerInterface.on_created_container
def routine(**kwargs):
	# The routine that will be executed when the event will be triggered
	...
```

Arguments provided to routines are different depending of the callback used.
That's why it is recommended to use `**kwargs` and to refer to the documentation to know the names of the passed parameters.

**NOTE** : When a client instance or raw socket is closed during a callback routine, the main server process will detect it, automatically terminating the session as a result. It is the same for container shell instances.

To have a proper example on how to use these decorators, see the _Basic server_ on the examples section.

```
@ServerInterface.on_client
```

> Triggered when a new client is connected and the keys are exchanged

_Provided parameters_ :

- `client_instance` : The `ClientInstance` instance representing the client

_Affiliated constant_ : `EVENT_CLIENT`

---

```
@ServerInterface.on_client_closed
```

> Triggered when a connected client was closed

_Provided parameters_ :

- `client_instance` : The `ClientInstance` instance Callback events representing the client

_Affiliated constant_ : `EVENT_CLIENT_CLOSED`

---

```
@ServerInterface.on_connection
```

> Triggered when a new client is connected and the keys have not been exchanged yet

_Provided parameters_ :

- `client_socket` : The raw client socket instance

_Affiliated constant_ : `EVENT_CONNECTION`

---

```
@ServerInterface.on_created_container
```

> Triggered when a new container instance is created

_Provided parameters_ :

- `client_instance` : The `ClientInstance` instance representing the affiliated client
- `container_instance` : The `ContainerInstance` instance of the created container

_Affiliated constant_ : `EVENT_CREATED_CONTAINER`

---

```
@ServerInterface.on_created_endpoint_shell
```

> Triggered when an endpoint shell was opened on a container

_Provided parameters_ :

- `endpoint_shell_instance` : The `EndpointShellInstance` on the container
- `container_instance` : The `ContainerInstance` instance representing the affiliated container
- `client_instance` : The `ClientInstance` instance representing the affiliated client

_Affiliated constant_ : `EVENT_CREATED_ENDPOINT_SHELL`

---

```
@ServerInterface.on_destroyed_container
```

> Triggered when a container was destroyed

_Provided parameters_ :

- `client_instance` : The `ClientInstance` instance representing the affiliated client
- `container_instance` : The `ContainerInstance` instance representing the affiliated container

_Affiliated constant_ : `EVENT_DESTROYED_CONTAINER`

---

```
@ServerInterface.on_malformed_request
```

> Triggered when the server has received a malformed request

_Provided parameters_ :

- `client_instance` : The `ClientInstance` instance representing the affiliated client
- `cerberus_error_dict` : The [cerberus error dict](https://docs.python-cerberus.org/en/stable/errors.html#errors-error-handling) depicting the error detected on the request

_Affiliated constant_ : `EVENT_MALFORMED_REQUEST`

---

```
@ServerInterface.on_request
```

> Triggered when the server receives a request

_Provided parameters_ :

- `client_instance` : The `ClientInstance` instance representing the affiliated client

_Affiliated constant_ : `EVENT_REQUEST`

---

```
@ServerInterface.on_runtime_error
```

> Triggered when an exception was raised during the server process

_Provided parameters_ :

- `name` : The name of the thread where the error occured
- `ex_class` : The exception class
- `traceback` : The full traceback of the exception as a string
- (optional) `client_instance` : The `ClientInstance` instance representing the affiliated client

_Affiliated constant_ : `EVENT_RUNTIME_ERROR`

---

```
@ServerInterface.on_started
```

> Triggered when the server is started and ready to operate

_Provided parameters_ :

- None

_Affiliated constant_ : `EVENT_STARTED`

---

```
@ServerInterface.on_stopped
```

> Triggered when the server was stopped

_Provided parameters_ :

- None

_Affiliated constant_ : `EVENT_STOPPED`

---

```
@ServerInterface.on_unknown_verb
```

> Triggered when the server has received an unknown or unsupported verb

_Provided parameters_ :

- `client_instance` : The `ClientInstance` instance representing the affiliated client

_Affiliated constant_ : `EVENT_UNKNOWN_VERB`
