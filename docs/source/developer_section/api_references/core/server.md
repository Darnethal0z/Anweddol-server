# Server

---

## Constants

In the module `anwdlserver.core.server` : 

### Default values

Constant name                   | Value   | Definition
------------------------------- | ------- | ----------
*DEFAULT_SERVER_BIND_ADDRESS*   | `""`    | The default server bind address.
*DEFAULT_SERVER_LISTEN_PORT*    | 6150    | The default server listen port.
*DEFAULT_CLIENT_TIMEOUT*        | 10      | The default client timeout.
*DEFAULT_DIE_ON_ERROR*          | `False` | Exit with the `0xDEAD` code if an error occured or not.
*DEFAULT_PASSIVE_MODE*          | `False` | Initialize the server in passive mode or not.
*DEFAULT_ASYNCHRONOUS*          | `False` | Handle the client asynchronoursly or not.

### Request constants

Constant name                 | Value       | Definition
----------------------------- | ----------- | ----------
*REQUEST_VERB_CREATE*         | `"CREATE"`  | Identifies a CREATE request.
*REQUEST_VERB_DESTROY*        | `"DESTROY"` | Identifies a DESTROY request.
*REQUEST_VERB_STAT*           | `"STAT"`    | Identifies a STAT request.

### Response constants

Constant name                 | Value                  | Definition
----------------------------- | ---------------------- | ----------
*RESPONSE_MSG_OK*             | `"OK"`                 | A response message announcing a success.
*RESPONSE_MSG_BAD_AUTH*       | `"Bad authentication"` | A response message announcing an authentication error.
*RESPONSE_MSG_BAD_REQ*        | `"Bad request"`        | A response message announcing that a bad request was received.
*RESPONSE_MSG_REFUSED_REQ*    | `"Refused request"`    | A response message announcing that the request was refused.
*RESPONSE_MSG_UNAVAILABLE*    | `"Unavailable"`        | A response message announcing an unavailable service.
*RESPONSE_MSG_UNSPECIFIED*    | `"Unspecified"`        | A response message announcing an unspecified error or information.
*RESPONSE_MSG_INTERNAL_ERROR* | `"Internal error"`     | A response message announcing that an internal error occured during the request processing.

### Events constants

Constant name                    | Value                           | Definition
-------------------------------- | ------------------------------- | ----------
*EVENT_CONTAINER_CREATED*        | `"on_container_created"`        | Identifies the event triggered when a new container instance was created.
*EVENT_CONTAINER_DOMAIN_STARTED* | `"on_container_domain_started"` | Identifies the event triggered when a container domain was started. 
*EVENT_CONTAINER_DOMAIN_STOPPED* | `"on_container_domain_stopped"` | Identifies the event triggered when a container domain was stopped. 
*EVENT_FORWARDER_CREATED*        | `"on_forwarder_created"`        | Identifies the event triggered when a new forwarder was created. 
*EVENT_FORWARDER_STARTED*        | `"on_forwarder_started"`        | Identifies the event triggered when a forwarder process was started. 
*EVENT_FORWARDER_STOPPED*        | `"on_forwarder_stopped"`        | Identifies the event triggered when a forwarder process was stopped. 
*EVENT_ENDPOINT_SHELL_CREATED*   | `"on_endpoint_shell_created"`   | Identifies the event triggered when an endpoint shell instance was created. 
*EVENT_ENDPOINT_SHELL_OPENED*    | `"on_endpoint_shell_opened"`    | Identifies the event triggered when an endpoint shell was opened on a container domain. 
*EVENT_ENDPOINT_SHELL_CLOSED*    | `"on_endpoint_shell_closed"`    | Identifies the event triggered when a prevoiusly opened endpoint shell was closed. 
*EVENT_SERVER_STARTED*           | `"on_server_started"`           | Identifies the event triggered when the server is started and ready to operate. 
*EVENT_SERVER_STOPPED*           | `"on_server_stopped"`           | Identifies the event triggered when the server was stopped. 
*EVENT_CLIENT_INITIALIZED*       | `"on_client_initialized"`       | Identifies the event triggered when a new client is ready for secure interactions. 
*EVENT_CLIENT_CLOSED*            | `"on_client_closed"`            | Identifies the event triggered when a client was closed. 
*EVENT_CONNECTION_ACCEPTED*      | `"on_connection_accepted"`      | Identifies the event triggered when a new socket connection happened. 
*EVENT_REQUEST*                  | `"on_request"`                  | Identifies the event triggered when a request is received. 
*EVENT_AUTHENTICATION_ERROR*     | `"on_authentication_error"`     | Identifies the event triggered when an authentication error occured. 
*EVENT_RUNTIME_ERROR*            | `"on_runtime_error"`            | Identifies the event triggered when an error occured during runtime. 
*EVENT_MALFORMED_REQUEST*        | `"on_malformed_request"`        | Identifies the event triggered when the server received a malformed request. 
*EVENT_UNHANDLED_VERB*           | `"on_unhandled_verb"`           | Identifies the event triggered when the server has received a request containing an unhandled verb.

### Event handler call context constants

Constant name                 | Value   | Definition
----------------------------- | ------- | ----------
*CONTEXT_NORMAL_PROCESS*      | 20      | Indicates that an event handler or a routine is called in a normal context.
*CONTEXT_AUTOMATIC_ACTION*    | 21      | Indicates that an event handler or a routine is called during an intern routine.
*CONTEXT_DEFERRED_CALL*       | 22      | Indicates that an event handler or a routine is called from an external source.
*CONTEXT_HANDLE_END*          | 23      | Indicates that an event handler or a routine is called during an handle termination.
*CONTEXT_ERROR*               | 24      | Indicates that an event handler or a routine is called in an error context.

## class *ServerInterface*

### Definition

```{class} anwdlserver.core.server.ServerInterface (runtime_container_iso_file_path, bind_address, listen_port, client_timeout, runtime_virtualization_interface, runtime_database_interface, runtime_port_forwarding_interface, runtime_rsa_wrapper)
```

This class is the main Anweddol server process. It connects every other core modules into a single one, so that they can all be used in a single class.

**Parameters** :

> ```{attribute} runtime_container_iso_file_path
> Type : str
> 
> The container ISO file path that will be used for containers.
> ```

> ```{attribute} bind_address
> Type : str
> 
> The bind address that the server will be using. Default is `0.0.0.0`.
> ```

> ```{attribute} listen_port
> Type : int
> 
> The listen port that the server will be using. Default is `6150`.
> ```

> ```{attribute} client_timeout
> Type : int
> 
> The timeout that will be applied to clients, exprimed in seconds. Default is `10`.
> ```

> ```{attribute} runtime_virtualization_interface
> Type : `VirtualizationInterface`
> 
> The `VirtualizationInterface` object that will be used by the server, or `None` to let the server generate one. Default is `None`.
> ```

> ```{attribute} runtime_database_interface
> Type : `DatabaseInterface`
> 
> The `DatabaseInterface` object that will be used by the server, or `None` to let the server generate one. Default is `None`.
> ```

> ```{attribute} runtime_port_forwarding_interface
> Type : `PortForwardingInterface`
> 
> The `PortForwardingInterface` object that will be used by the server, or `None` to let the server generate one. Default is `None`.
> ```

> ```{attribute} runtime_rsa_wrapper
> Type : `RSAWrapper`
> 
> The `RSAWrapper` object that will be used by the server, or `None` to let the server generate one. Default is `None`.
> ```

> ```{attribute} passive_mode
> Type : bool
> 
> Initialize the server as passive or not (see below).
> ```

```{warning}
If the parameter `passive_mode` is set to `True`, the server will not initialize any client management interfaces.
The server will run normally, except that : 

- The runtime RSA wrapper will not be used ;
- No listen interface will be created ;

You can access default request handlers with the `executeRequestHandler` method.

> *This mode permits the `ServerInterface` class features external usage with a deferred client system.*
```

```{tip}
This class can be used in a 'with' statement.
```

```{note} 
The container ISO path must point to a valid [ISO image](../../../administration_guide/container_iso.md).

The method `stopServer()` will be called on `__del__` method if the server is running.
```

### General usage

```{classmethod} isRunning()
```

Check if the server is running.

**Parameters** :

> None.

**Return value** : 

> Type : bool
>
> `True` if the server is running, `False` otherwise.

---

```{classmethod} getRuntimeContainerISOFilePath()
```

Get the runtime container ISO file path.

**Parameters** : 

> None.

**Return value** : 

> Type : str
>
> The runtime ISO file path used by the server.

---

```{classmethod} getRuntimeDatabaseInterface()
```

Get the runtime `DatabaseInterface` object.

**Parameters** : 

> None.

**Return value** : 

> Type : `DatabaseInterface`
>
> The `DatabaseInterface` object used by the server.

---

```{classmethod} getRuntimeVirtualizationInterface()
```

Get the runtime `VirtualizationInterface` object.

**Parameters** : 

> None.

**Return value** : 

> Type : `VirtualizationInterface`
>
> The `VirtualizationInterface` object used by the server.

---

```{classmethod} getRuntimeRSAWrapper()
```

Get the runtime `RSAWrapper` object.

**Parameters** : 

> None.

**Return value** : 

> Type : `RSAWrapper`
>
> The `RSAWrapper` object used by the server.

---

```{classmethod} getRuntimePortForwardingInterface()
```

Get the runtime `PortForwardingInterface` object.

**Parameters** : 

> None.

**Return value** : 

> Type : `PortForwardingInterface`
>
> The `PortForwardingInterface` object used by the server.

---

```{classmethod} getRuntimeStatistics()
```

Return the actual runtime statistics.

**Parameters** : 

> None.

**Return value** : 

> Type : tuple
>
> A tuple containing the server runtime statistics :

> ```
> (
> 	is_running,
> 	recorded_runtime_errors_amount,
> 	uptime
> )
> ```
> 
> - *is_running*
> 
>	Type : bool
> 
>   Boolean value set to `True` if the server is currently running, `False` otherwise.
> 
> - *recorded_runtime_errors_amount*
> 
>	Type : int
> 
>   The amount of errors recorded during the runtime.
> 
> - *uptime*
> 
>	Type : int
> 
>   The server uptime, exprimed in seconds.

---

```{classmethod} getRequestHandler(verb)
```

Get a request handler.

**Parameters** : 

> ```{attribute} verb
> Type : str
> 
> The verb to get the corresponding handler from.
> ```

**Return value** : 

> Type : [callable](https://docs.python.org/3/glossary.html#term-callable) | `NoneType`
>
> The request handler object, or `None` if there is none.

---

```{classmethod} getEventHandler(event)
```

Get an event handler.

**Parameters** : 

> ```{attribute} event
> Type : str
> 
> The event to get the corresponding handler from.
> ```

**Return value** : 

> Type : [callable](https://docs.python.org/3/glossary.html#term-callable) | `NoneType`
>
> The event handler object, or `None` if there is none.

---

```{classmethod} setRuntimeContainerISOFilePath(iso_file_path)
```

Set the runtime container ISO file path.

**Parameters** :

> ```{attribute} iso_file_path
> Type : str
> 
> The container ISO file path to set.
> ```

**Return value** : 

> `None`.

---

```{classmethod} setRuntimeDatabaseInterface(database_interface)
```

Set the runtime `DatabaseInterface` object.

**Parameters** :

> ```{attribute} database_interface
> Type : `DatabaseInterface`
> 
> The `DatabaseInterface` object to set.
> ```

**Return value** : 

> `None`.

---

```{classmethod} setRuntimeVirtualizationInterface(virtualization_interface)
```

Set the runtime `VirtualizationInterface` object.

**Parameters** :

> ```{attribute} virtualization_interface
> Type : `VirtualizationInterface`
> 
> The `VirtualizationInterface` object to set.
> ```

**Return value** : 

> `None`.

---

```{classmethod} setRuntimeRSAWrapper(rsa_wrapper)
```

Set the runtime `RSAWrapper` object.

**Parameters** :

> ```{attribute} rsa_wrapper
> Type : `RSAWrapper`
> 
> The `RSAWrapper` object to set.
> ```

**Return value** : 

> `None`.

---

```{classmethod} setRuntimePortForwardingInterface(port_forwarding_interface)
```

Set the runtime `PortForwardingInterface` object.

**Parameters** :

> ```{attribute} port_forwarding_interface
> Type : `PortForwardingInterface`
> 
> The `PortForwardingInterface` object to set.
> ```

**Return value** : 

> `None`.

### Request / client handling

```{classmethod} setRequestHandler(verb, routine)
```

Set a request handler.

**Parameters** :

> ```{attribute} verb
> Type : str
> 
> The request verb to handle. It can be a custom one or a pre-defined normalized one :
> ```

>> ```{attribute} REQUEST_VERB_CREATE
>> Handle a CREATE request.
>> ```
>> 
>> ```{attribute} REQUEST_VERB_STAT
>> Handle a STAT request.
>> ```
>> 
>> ```{attribute} REQUEST_VERB_DESTROY
>> Handle a DESTROY request.
>> ```

> ```{attribute} routine
> Type : [callable](https://docs.python.org/3/glossary.html#term-callable)
> 
> A callable object that will be called when a received request verb is equal to `verb` value.
> ```

**Return value** : 

> `None`.

```{note}
When the `routine` object is called, the `ClientInstance` object of the session will be passed in a `client_instance` parameter.
```

---

```{classmethod} handleClient(client_instance, asynchronous)
```

Handle a client.

**Parameters** :

> ```{attribute} client_instance
> Type : `ClientInstance`
> 
> The `ClientInstance` object representing the client to handle. It must be an active client.
> ```

> ```{attribute} asynchronous
> Type : bool
> 
> `True` to handle the client asynchronously, `False` to handle it synchronously. Default is `False`
> ```

**Return value** :

> `None`.

### Server lifecycle control

```{classmethod} startServer()
```

Start the server.

**Parameters** :

> None.

**Return value** : 

> `None`.

```{note} 
If the `passive_mode` parameter on initialization is set to `False`, this method will block I/O, it must be the last instruction to execute on parent thread.
```

---

```{classmethod} stopServer(die_on_error)
```

Stop the server.

**Parameters** :

> ```{attribute} die_on_error
> Type : bool
> 
> `True` to exit the process if an error occured during the server termination routine, `False` otherwise. Default is `False`.
> ```

**Return value** : 

> `None`.

```{note}
This method is automatically called within the `__del__` method, but it is programatically better to call it naturally.
```

### Manual handler execution

```{classmethod} executeRequestHandler(verb, client_instance, data, **kwargs)
```

Execute a request handler.

**Parameters** :

> ```{attribute} verb
> Type : str
> 
> The verb corresponding to the handler to execute. It can be a custom one or a pre-defined normalized one :
> ```

>> ```{attribute} REQUEST_VERB_CREATE
>> Handle a CREATE request.
>> ```
>> 
>> ```{attribute} REQUEST_VERB_STAT
>> Handle a STAT request.
>> ```
>> 
>> ```{attribute} REQUEST_VERB_DESTROY
>> Handle a DESTROY request.
>> ```

> ```{attribute} client_instance
> Type : `ClientInstance`
> 
> The `ClientInstance` object representing the client to handle. Default is `None`.
> ```

> ```{attribute} data
> Type : dict
> 
> The data dictionary to pass to handlers. Default is an empty dict.
> ```

> ```{attribute} **kwargs
> 
> A dictionary for keywords arguments to pass in the request handler function.
> ```

**Return value** : 

> Type : dict | `NoneType`
>
> A response dictionary as a normalized [Response format](../../../technical_specifications/core/communication.md) if the `ServerInterface` instance was initialized with the `passive_mode` parameter set to `True` or `client_instance` is set to `None`, `None` otherwise.

```{note}
The parameter `data` must be set with appropriate credentials for `DESTROY` requests.

If the `**kwargs` dictionary is set, its content will be available in every relevant event handlers parameter, in the `data` parameter.
```

```{tip}
This method is made to enable access to default request handlers without specifying a `ClientInstance` object in the process.
```

---

```{classmethod} triggerEvent(event, context, data)
```

Execute an event handler.

**Parameters** :

> ```{attribute} event
> Type : str
> 
> The event to trigger.
> ```

> ```{attribute} context
> Type : int
> 
> The context in which the event is triggered. It can be 5 possible values : 
> ```

>> ```{attribute} CONTEXT_NORMAL_PROCESS
>> Indicates that the event is triggered in a normal process execution.
>> ```

>> ```{attribute} CONTEXT_HANDLE_END
>> Indicates that the event is triggered after the end of a client handling, there is no future operations after the call.
>> ```

>> ```{attribute} CONTEXT_AUTOMATIC_ACTION
>> Indicates that the event is triggered in a subroutine.
>> ```

>> ```{attribute} CONTEXT_DEFERRED_CALL
>> Indicates that the event is triggered from an external process.
>> ```

>> ```{attribute} CONTEXT_ERROR
>> Indicates that the event is triggered because an error occured in the normal process.
>> ```

> ```{attribute} data
> Type : str
> 
> The dictionary containing additional values related to the context.
> ```

**Return value** : 

> Type : Any
>
> If the `passive_mode` parameter is set to `True` during `ServerInterface` initialization, this method returns whatever the handler routine bound to this event returns: the default handler routines returns a response dictionary as a normalized [Response format](../../../technical_specifications/core/communication.md). 
>
> Otherwise it returns `-1` if a client instance is specified in the `data` parameters and that this client is closed, else `None`.

**Possible raise classes** :

> ```{exception} RuntimeError
> An error occured due to a failed internal action.
> 
> Raised in this method if the specified event does not exists.
> ```

```{warning}
If the routine returns any value, this value will be available only if the `ServerInterface` `passive_mode` parameter is set to `True`.
```

### Events handling

You can interact with the server process via events. Those events can be bind to callable objects via 2 techniques : 

#### Set custom event handler via the method

```{classmethod} setEventHandler(event, routine)
```

Set an event handler. This is the method alternative of event decorators (see below).

**Parameters** :

> ```{attribute} event
> Type : str
> 
> The event to handle. See the section below to get the constant names.
> ```

> ```{attribute} routine
> Type : [callable](https://docs.python.org/3/glossary.html#term-callable)
> 
> A callable object that will be called when the `event` event is triggered.
> ```

**Return value** : 

> `None`.

```{tip}
You can directly pass the event constant value in the `event` parameter rather than importing the constant.

For example, if you want to use the `EVENT_CONTAINER_DOMAIN_STARTED` constant, just put the `"on_container_domain_started"` string.

See the constants definitions at the top of the page to know every constants and their values.
```

#### Set custom event handler via decorators

```
# The decorator depicting the event. Here EVENT_CONTAINER_CREATED
@ServerInterface.on_container_created
def routine(context: int, data: dict):
	# The routine that will be executed when the event will be triggered
	...
```

The server will execute the given routine function passing 2 parameters : 

> ```{attribute} context
> Type : str
> 
> The context in which the routine is called. It can be 5 possible values : 
> ```

>> ```{attribute} CONTEXT_NORMAL_PROCESS
>> Indicates that the routine is called in a normal process execution.
>> ```

>> ```{attribute} CONTEXT_HANDLE_END
>> Indicates that the routine is called after the end of a client handling, there is no future operations after the call.
>> ```

>> ```{attribute} CONTEXT_AUTOMATIC_ACTION
>> Indicates that the routine is called in a subroutine.
>> ```

>> ```{attribute} CONTEXT_DEFERRED_CALL
>> Indicates that the routine is called from an external process.
>> ```

>> ```{attribute} CONTEXT_ERROR
>> Indicates that the routine is called because an error occured in the normal process.
>> ```

> ```{attribute} data
> Type : str
> 
> The dictionary containing additional values related to the context. See below to know the keys and values set in each cases (in **Provided values** sections).
> ```

```{note}
Routine execution is integrated with the server process itself, passing its own values and objects in its parameters so that execution can be as transparent as possible. 
```

```{warning}
If the parameter `client_instance` representing a client is detected as closed after the routine execution, the server will instantly terminate its process since it will interpret it as a handle termination notice.

If the routine returns any value, this value will be available only if the `ServerInterface` `passive_mode` parameter is set to `True`.
```

##### Decorators references

```{function} @ServerInterface.on_container_created
```

Called when a new container instance was created.

**Affiliated event constant** : 

`EVENT_CONTAINER_CREATED`

**Provided values** :

```
{
	"client_instance": CLIENT_INSTANCE,
	"container_instance": CONTAINER_INSTANCE,
}
```

- *CLIENT_INSTANCE*

  Type : `ClientInstance`

  The `ClientInstance` object representing the handled client.

- *CONTAINER_INSTANCE*

  Type : `ContainerInstance`
  
  The `ContainerInstance` object representing the created container.

---

```{function} @ServerInterface.on_container_domain_started
```

Called when a container domain was started.

**Affiliated event constant** : 

`EVENT_CONTAINER_DOMAIN_STARTED`

**Provided values** :

```
{
	"client_instance": CLIENT_INSTANCE,
	"container_instance": CONTAINER_INSTANCE,
}
```

- *CLIENT_INSTANCE*

  Type : `ClientInstance`

  The `ClientInstance` object representing the handled client.

- *CONTAINER_INSTANCE*

  Type : `ContainerInstance`
	
  The `ContainerInstance` object representing the container.

---

```{function} @ServerInterface.on_container_domain_stopped
```

Called when a container domain was stopped.

**Affiliated event constant** : 

`EVENT_CONTAINER_DOMAIN_STOPPED`

**Provided values** :

```
{
	"container_instance": CONTAINER_INSTANCE,
}
```

- *CONTAINER_INSTANCE*

	Type : `ContainerInstance`

	The `ContainerInstance` object representing the container.

Note that more keys can be provided :

```
{
	"client_instance": CLIENT_INSTANCE,
}
```

- *CLIENT_INSTANCE*

  Type : `ClientInstance`

  The `ClientInstance` object representing the handled client.

---

```{function} @ServerInterface.on_forwarder_created
```

Called when a new forwarder was created.

**Affiliated event constant** : 

`EVENT_FORWARDER_CREATED`

**Provided values** :

```
{
	"client_instance": CLIENT_INSTANCE,
	"forwarder_instance": FORWARDER_INSTANCE,
}
```

- *CLIENT_INSTANCE*

  Type : `ClientInstance`

  The `ClientInstance` object representing the handled client.

- *FORWARDER_INSTANCE*

  Type : `ForwarderInstance`

  The `ForwarderInstance` object representing the forwarder.

---

```{function} @ServerInterface.on_forwarder_started
```

Called when a forwarder process was started.

**Affiliated event constant** : 

`EVENT_FORWARDER_STARTED`

**Provided values** :

```
{
	"client_instance": CLIENT_INSTANCE,
	"forwarder_instance": FORWARDER_INSTANCE,
}
```

- *CLIENT_INSTANCE*

  Type : `ClientInstance`

  The `ClientInstance` object representing the handled client.

- *FORWARDER_INSTANCE*

  Type : `ForwarderInstance`

  The `ForwarderInstance` object representing the forwarder.

---

```{function} @ServerInterface.on_forwarder_stopped
```

Called when a forwarder process was stopped.

**Affiliated event constant** : 

`EVENT_FORWARDER_STOPPED`

---

```{function} @ServerInterface.on_endpoint_shell_created
```

Called when an endpoint shell instance was created.

**Affiliated event constant** : 

`EVENT_ENDPOINT_SHELL_CREATED`

**Provided values** :

```
{
	"client_instance": CLIENT_INSTANCE,
	"endpoint_shell_instance": ENDPOINT_SHELL_INSTANCE,
}
```

- *CLIENT_INSTANCE*

  Type : `ClientInstance`

  The `ClientInstance` object representing the handled client.

- *ENDPOINT_SHELL_INSTANCE*

  Type : `EndpointShellInstance`

  The `EndpointShellInstance` object.

---

```{function} @ServerInterface.on_endpoint_shell_opened
```

Called when an endpoint shell was opened on a container domain.

**Affiliated event constant** : 

`EVENT_ENDPOINT_SHELL_OPENED`

**Provided values** :

```
{
	"client_instance": CLIENT_INSTANCE,
	"endpoint_shell_instance": ENDPOINT_SHELL_INSTANCE,
}
```

- *CLIENT_INSTANCE*

  Type : `ClientInstance`

  The `ClientInstance` object representing the handled client.

- *ENDPOINT_SHELL_INSTANCE*

  Type : `EndpointShellInstance`

  The `EndpointShellInstance` object.

---

```{function} @ServerInterface.on_endpoint_shell_closed
```

Called when a prevoiusly opened endpoint shell was closed.

**Affiliated event constant** : 

`EVENT_ENDPOINT_SHELL_CLOSED`

**Provided values** :

```
{
	"client_instance": CLIENT_INSTANCE,
	"endpoint_shell_instance": ENDPOINT_SHELL_INSTANCE,
}
```

- *CLIENT_INSTANCE*

  Type : `ClientInstance`

  The `ClientInstance` object representing the handled client.

- *ENDPOINT_SHELL_INSTANCE*

  Type : `EndpointShellInstance`

  The `EndpointShellInstance` object.

---

```{function} @ServerInterface.on_server_started
```

Called when the server is started and ready to operate.

**Affiliated event constant** : 

`EVENT_SERVER_STARTED`

**Provided values** : 

None.

---

```{function} @ServerInterface.on_server_stopped
```

Called when the server was stopped.

**Affiliated event constant** : 

`EVENT_SERVER_STOPPED`

**Provided values** : 

None.

---

```{function} @ServerInterface.on_client_initialized
```

Called when a new client is ready for secure interactions.

**Affiliated event constant** : 

`EVENT_CLIENT_INITIALIZED`

**Provided values** :

```
{
	"client_instance": CLIENT_INSTANCE,
}
```

- *CLIENT_INSTANCE*

  Type : `ClientInstance`

  The `ClientInstance` object representing the initialized client.

---

```{function} @ServerInterface.on_client_closed
```

Called when a client was closed.

**Affiliated event constant** : 

`EVENT_CLIENT_CLOSED`

**Provided values** :

```
{
	"client_instance": CLIENT_INSTANCE,
}
```

- *CLIENT_INSTANCE*

  Type : `ClientInstance`

  The `ClientInstance` object representing the handled client.

---

```{function} @ServerInterface.on_connection_accepted
```

Called when a new socket connection happened.

**Affiliated event constant** : 

`EVENT_CONNECTION_ACCEPTED`

**Provided values** :

```
{
	"client_socket": CLIENT_SOCKET,
}
```

- *CLIENT_SOCKET*

  Type : `socket.socket`

  The raw client socket object.

---

```
@ServerInterface.on_request
```

Called when a request is received.

**Affiliated event constant** : 

`EVENT_REQUEST`

**Provided values** :

```
{
	"client_instance": CLIENT_INSTANCE,
}
```

- *CLIENT_INSTANCE*

  Type : `ClientInstance`

  The `ClientInstance` object representing the handled client.

---

```
@ServerInterface.on_authentication_error
```

Called when an authentication error occured.

**Affiliated event constant** : 

`EVENT_AUTHENTICATION_ERROR`

**Provided values** :

```
{
	"client_instance": CLIENT_INSTANCE,
}
```

- *CLIENT_INSTANCE*

  Type : `ClientInstance`

  The `ClientInstance` object representing the handled client.

---

```
@ServerInterface.on_runtime_error
```

Called when an error occured during runtime.

**Affiliated event constant** : 

`EVENT_RUNTIME_ERROR`

**Provided values** :

```
{
	"exception_object": EXCEPTION_OBJECT,
	"traceback": TRACEBACK,
}
```

- *EXCEPTION_OBJECT*

  Type : class

  The exception class object.

- *TRACEBACK*

  Type : str

  The full traceback of the exception as a string.

Note that more keys can be provided depending on the context :

```
{
	"client_socket": CLIENT_SOCKET,
	"client_instance": CLIENT_INSTANCE,
}
```

- *CLIENT_SOCKET*

  Type : `socket.socket`

  The raw client socket object.

- *CLIENT_INSTANCE*

  Type : `ClientInstance`

  The `ClientInstance` object representing the handled client.

---

```
@ServerInterface.on_malformed_request
```

Called when the server received a malformed request.

**Affiliated event constant** : 

`EVENT_MALFORMED_REQUEST`

**Provided values** :

```
{
	"client_instance": CLIENT_INSTANCE,
	"errors_dict": ERRORS_DICT,
}
```

- *CLIENT_INSTANCE*

  Type : `ClientInstance`

  The `ClientInstance` object representing the handled client.

- *ERRORS_DICT*

  Type : dict

  A dictionary depicting the errors in the received request, according to the [Cerberus](https://docs.python-cerberus.org/en/stable/errors.html) error format.

---

```
@ServerInterface.on_unhandled_verb
```

Called when the server has received a request containing an unhandled verb.

**Affiliated event constant** : 

`EVENT_UNHANDLED_VERB`

**Provided values** :

```
{
	"client_instance": CLIENT_INSTANCE,
}
```

- *CLIENT_INSTANCE*

  Type : `ClientInstance`

  The `ClientInstance` object representing the handled client.

### Undocumented methods

- `__del__()`
- `__enter__()`
- `__exit__(type, value, traceback)`
- `_format_traceback(exception)`
- `_initialize_listen_interface()`
- `_terminate_listen_interface()`
- `_execute_event_handler(event, context, data={})`
- `_store_container(container_instance, forwarder_instance)`
- `_delete_container(container_instance)`
- `_delete_container_on_domain_shutdown_routine()`
- `_delete_all_containers()`
- `_start_server()`
- `_stop_server(die_on_error=False)`
- `_handle_create_request(client_instance=None, passive_execution=False, **kwargs)`
- `_handle_destroy_request(client_instance=None, passive_execution=False, credentials_dict={}, **kwargs)`
- `_handle_stat_request(client_instance=None, passive_execution=False, **kwargs)`
- `_handle_new_client(client_instance)`
- `_main_server_loop_routine()`