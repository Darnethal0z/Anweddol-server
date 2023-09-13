# Server

---

## class *ServerInterface*

### Definition

```{class} anwdlserver.core.server.ServerInterface (runtime_container_iso_file_path, bind_address, listen_port, client_timeout, runtime_virtualization_interface, runtime_database_interface, runtime_port_forwarding_interface, runtime_rsa_wrapper)
```

This class is the main Anweddol server class, it contains every basic features that a server must provide in order to be functional.

**Parameters** :

> ```{attribute} runtime_container_iso_file_path
> > Type : str
> 
> The container ISO file path that will be used for containers.
> ```

> ```{note} 
> The container ISO path must point to a valid [ISO image](../../../administration_guide/container_iso.md).
> ```

> ```{attribute} bind_address
> > Type : str
> 
> The bind address that the server will be using. Default is `0.0.0.0`.
> ```

> ```{attribute} listen_port
> > Type : int
> 
> The listen port that the server will be using. Default is `6150`.
> ```

> ```{attribute} client_timeout
> > Type : int
> 
> The timeout that will be applied to clients, exprimed in seconds. Default is `10`.
> ```

> ```{attribute} runtime_virtualization_interface
> > Type : `VirtualizationInterface`
> 
> The `VirtualizationInterface` object that will be used by the server, or `None` to let > the server generate one. Default is `None`.
> ```

> ```{attribute} runtime_database_interface
> > Type : `DatabaseInterface`
> 
> The `DatabaseInterface` object that will be used by the server, or `None` to let the server generate one. Default is `None`.
> ```

> ```{attribute} runtime_port_forwarding_interface
> > Type : `PortForwardingInterface`
> 
> The `PortForwardingInterface` object that will be used by the server, or `None` to let the server generate one. Default is `None`.
> ```

> ```{attribute} runtime_rsa_wrapper
> > Type : `RSAWrapper`
> 
> The `RSAWrapper` object that will be used by the server, or `None` to let the server generate one. Default is `None`.
> ```

```{note}
The method `stopServer()` will be called on `__del__` method if the server is running.
```

### General usage

```{classmethod} getRuntimeContainerISOFilePath()
```

Get the runtime container ISO file path.

**Parameters** : 

> None.

**Return value** : 

> The runtime ISO file path used by the server.

---

```{classmethod} getRuntimeDatabaseInterface()
```

Get the runtime `DatabaseInterface` object.

**Parameters** : 

> None.

**Return value** : 

> The `DatabaseInterface` object used by the server.

---

```{classmethod} getRuntimeVirtualizationInterface()
```

Get the runtime `VirtualizationInterface` object.

**Parameters** : 

> None.

**Return value** : 

> The `VirtualizationInterface` object used by the server.

---

```{classmethod} getRuntimeRSAWrapper()
```

Get the runtime `RSAWrapper` object.

**Parameters** : 

> None.

**Return value** : 

> The `RSAWrapper` object used by the server.

---

```{classmethod} getRuntimePortForwardingInterface()
```

Get the runtime `PortForwardingInterface` object.

**Parameters** : 

> None.

**Return value** : 

> The `PortForwardingInterface` object used by the server.

---

```{classmethod} getRuntimeStatistics()
```

Return the actual runtime statistics.

**Parameters** : 

> None.

**Return value** : 

> A tuple containing the server runtime statistics :

> ```
> (
> 	is_running,
> 	recorded_runtime_errors_amount,
> 	uptime
> )
> ```
> 
> - *is_running* (Type : bool)
> 
>   Boolean value set to `True` if the server is currently running, `False` otherwise.
> 
> - *recorded_runtime_errors_amount* (Type : int)
> 
>   The amount of errors recorded during the runtime.
> 
> - *uptime* (Type : int)
> 
>   The server uptime, exprimed in seconds.

---

```{classmethod} getRequestHandler(verb)
```

Get a request handler.

**Parameters** : 

> ```{attribute} verb
> > Type : str
> 
> The verb to get the corresponding handler from.
> ```

**Return value** : 

> The request handler object, or `None` if there is none.

---

```{classmethod} getEventHandler(event)
```

Get an event handler.

**Parameters** : 

> ```{attribute} event
> > Type : str
> 
> The event to get the corresponding handler from.
> ```

**Return value** : 

> The event handler object, or `None` if there is none.

---

```{classmethod} setRuntimeContainerISOFilePath(iso_file_path)
```

Set the runtime container ISO file path.

**Parameters** :

> ```{attribute} iso_file_path
> > Type : str
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
> > Type : `DatabaseInterface`
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
> > Type : `VirtualizationInterface`
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
> > Type : `RSAWrapper`
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
> > Type : `PortForwardingInterface`
> 
> The `PortForwardingInterface` object to set.
> ```

**Return value** : 

> `None`.

### Request handling

```{classmethod} setRequestHandler(verb, routine)
```

Set a request handler.

**Parameters** :

> ```{attribute} verb
> > Type : str
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
> > Type : [callable](https://docs.python.org/3/glossary.html#term-callable)
> 
> A callable object that will be called when a received request verb is equal to `verb` value.
> ```

**Return value** : 

> `None`.

### Server lifecycle control

```{classmethod} startServer(asynchronous)
```

Start the server.

**Parameters** :

> None.

**Return value** : 

> `None`.

```{note} 
The parent thread execution will be deadlocked if called.
```

---

```{classmethod} stopServer(die_on_error)
```

Stop the server.

**Parameters** :

> ```{attribute} die_on_error
> > Type : bool
> 
> `True` to exit the process if an error occured during the server termination routine, `False` otherwise. Default is `False`.
> ```

**Return value** : 

> `None`.

```{note}
This method is automatically called within the `__del__` method, but it is programatically better to call it naturally.
```

### Events handling

You can interact with the server process via events. Those events can be bind to callable objects via 2 techniques : 

#### Set custom event handler via the method

```{classmethod} setEventHandler(event, routine)
```

Set an event handler. This is the method alternative of event decorators (see below).

**Parameters** :

> ```{attribute} event
> > Type : str
> 
> The event to handle. See the section below to get the constant names.
> ```

> ```{attribute} routine
> > Type : [callable](https://docs.python.org/3/glossary.html#term-callable)
> 
> A callable object that will be called when the `event` event is triggered.
> ```

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
> > Type : str
> 
> The context in which the routine is called. It can be 4 possible values : 
> ```

>> ```{attribute} CONTEXT_NORMAL_PROCESS
>> The routine have been called in a normal process execution.
>> ```

>> ```{attribute} CONTEXT_HANDLE_END
>> The routine have been called after the end of a client handling, there is no future operations after the call.
>> ```

>> ```{attribute} CONTEXT_ERROR
>> The routine have been called because an error occured in the normal process.
>> ```

> ```{attribute} data
> > Type : str
> 
> The dictionary containing additional values related to the context. See below to know the keys and values set in each cases (in **Provided values** sections).
> ```

```{note}
Routine execution is integrated with the server process itself, passing its own values and objects in its parameters so that execution can be as transparent as possible. 
```

```{warning}
If the parameter `client_instance` representing a client is detected as closed after the routine execution, the server will instantly terminate its process since it will interpret it as a handle termination notice.
```

##### Decorators references

```{function} @ServerInterface.on_container_created
```

Called when a new container was created.

**Affiliated event constant** : `EVENT_CONTAINER_CREATED`

**Provided values** :

```
{
	"client_instance": CLIENT_INSTANCE,
	"container_instance": CONTAINER_INSTANCE,
}
```

- *CLIENT_INSTANCE* (Type : `ClientInstance`)

  The `ClientInstance` object representing the handled client.

- *CONTAINER_INSTANCE* (Type : `ContainerInstance`)
  
  The `ContainerInstance` object representing the created container.

---

```{function} @ServerInterface.on_container_domain_started
```

Called when a container domain was started.

**Affiliated event constant** : `EVENT_CONTAINER_DOMAIN_STARTED`

**Provided values** :

```
{
	"client_instance": CLIENT_INSTANCE,
	"container_instance": CONTAINER_INSTANCE,
}
```

- *CLIENT_INSTANCE* (Type : `ClientInstance`)

  The `ClientInstance` object representing the handled client.

- *CONTAINER_INSTANCE* (Type : `ContainerInstance`)
	
	The `ContainerInstance` object representing the container.

---

```{function} @ServerInterface.on_container_domain_stopped
```

Called when a container domain was stopped.

**Affiliated event constant** : `EVENT_CONTAINER_DOMAIN_STOPPED`

**Provided values** :

```
{
	"container_instance": CONTAINER_INSTANCE,
}
```

- *CONTAINER_INSTANCE* (Type : `ContainerInstance`)

	The `ContainerInstance` object representing the container.

Note that more keys can be provided :

```
{
	"client_instance": CLIENT_INSTANCE,
}
```

- *CLIENT_INSTANCE* (Type : `ClientInstance`)

  The `ClientInstance` object representing the handled client.

---

```{function} @ServerInterface.on_forwarder_created
```

Called when a new forwarder was created.

**Affiliated event constant** : `EVENT_FORWARDER_CREATED`

**Provided values** :

```
{
	"client_instance": CLIENT_INSTANCE,
	"forwarder_instance": FORWARDER_INSTANCE,
}
```

- *CLIENT_INSTANCE* (Type : `ClientInstance`)

  The `ClientInstance` object representing the handled client.

- *FORWARDER_INSTANCE* (Type : `ForwarderInstance`)

  The `ForwarderInstance` object representing the forwarder.

---

```{function} @ServerInterface.on_forwarder_started
```

Called when a forwarder process was started.

**Affiliated event constant** : `EVENT_FORWARDER_STARTED`

**Provided values** :

```
{
	"client_instance": CLIENT_INSTANCE,
	"forwarder_instance": FORWARDER_INSTANCE,
}
```

- *CLIENT_INSTANCE* (Type : `ClientInstance`)

  The `ClientInstance` object representing the handled client.

- *FORWARDER_INSTANCE* (Type : `ForwarderInstance`)

  The `ForwarderInstance` object representing the forwarder.

---

```{function} @ServerInterface.on_forwarder_stopped
```

Called when a forwarder process was stopped.

**Affiliated event constant** : `EVENT_FORWARDER_STOPPED`

---

```{function} @ServerInterface.on_endpoint_shell_created
```

Called when an endpoint shell was created.

**Affiliated event constant** : `EVENT_ENDPOINT_SHELL_CREATED`

**Provided values** :

```
{
	"client_instance": CLIENT_INSTANCE,
	"endpoint_shell_instance": ENDPOINT_SHELL_INSTANCE,
}
```

- *CLIENT_INSTANCE* (Type : `ClientInstance`)

  The `ClientInstance` object representing the handled client.

- *ENDPOINT_SHELL_INSTANCE* (Type : `EndpointShellInstance`)

  The `EndpointShellInstance` object.

---

```{function} @ServerInterface.on_endpoint_shell_opened
```

Called when an endpoint shell was opened on a container.

**Affiliated event constant** : `EVENT_ENDPOINT_SHELL_OPENED`

**Provided values** :

```
{
	"client_instance": CLIENT_INSTANCE,
	"endpoint_shell_instance": ENDPOINT_SHELL_INSTANCE,
}
```

- *CLIENT_INSTANCE* (Type : `ClientInstance`)

  The `ClientInstance` object representing the handled client.

- *ENDPOINT_SHELL_INSTANCE* (Type : `EndpointShellInstance`)

  The `EndpointShellInstance` object.

---

```{function} @ServerInterface.on_endpoint_shell_closed
```

Called when an prevoiusly opened endpoint shell was closed.

**Affiliated event constant** : `EVENT_ENDPOINT_SHELL_CLOSED`

**Provided values** :

```
{
	"client_instance": CLIENT_INSTANCE,
	"endpoint_shell_instance": ENDPOINT_SHELL_INSTANCE,
}
```

- *CLIENT_INSTANCE* (Type : `ClientInstance`)

  The `ClientInstance` object representing the handled client.

- *ENDPOINT_SHELL_INSTANCE* (Type : `EndpointShellInstance`)

  The `EndpointShellInstance` object.

---

```{function} @ServerInterface.on_server_started
```

Called when the server is started and ready to operate.

**Affiliated event constant** : `EVENT_SERVER_STARTED`

**Provided values** : None.

---

```{function} @ServerInterface.on_server_stopped
```

Called when the server was stopped.

**Affiliated event constant** : `EVENT_SERVER_STOPPED`

**Provided values** : None.

---

```{function} @ServerInterface.on_client_initialized
```

Called when a new client is ready for secure interactions.

**Affiliated event constant** : `EVENT_CLIENT_INITIALIZED`

**Provided values** : None.

```
{
	"client_instance": CLIENT_INSTANCE,
}
```

- *CLIENT_INSTANCE* (Type : `ClientInstance`)

  The `ClientInstance` object representing the initialized client.

---

```{function} @ServerInterface.on_client_closed
```

Called when a client was closed.

**Affiliated event constant** : `EVENT_CLIENT_CLOSED`

**Provided values** :

```
{
	"client_instance": CLIENT_INSTANCE,
}
```

- *CLIENT_INSTANCE* (Type : `ClientInstance`)

  The `ClientInstance` object representing the handled client.

---

```{function} @ServerInterface.on_connection_accepted
```

Called when a new socket connection happened.

**Affiliated event constant** : `EVENT_CONNECTION_ACCEPTED`

**Provided values** :

```
{
	"client_socket": CLIENT_SOCKET,
}
```

- *CLIENT_SOCKET* (Type : `socket.socket`)

  The raw client socket object.

---

```
@ServerInterface.on_request
```

Called when a request is received.

**Affiliated event constant** : `EVENT_REQUEST`

**Provided values** :

```
{
	"client_instance": CLIENT_INSTANCE,
}
```

- *CLIENT_INSTANCE* (Type : `ClientInstance`)

  The `ClientInstance` object representing the handled client.

---

```
@ServerInterface.on_authentication_error
```

Called when an authentication error occured.

**Affiliated event constant** : `EVENT_AUTHENTICATION_ERROR`

**Provided values** :

```
{
	"client_instance": CLIENT_INSTANCE,
}
```

- *CLIENT_INSTANCE* (Type : `ClientInstance`)

  The `ClientInstance` object representing the handled client.

---

```
@ServerInterface.on_runtime_error
```

Called when an error occured during runtime.

**Affiliated event constant** : `EVENT_RUNTIME_ERROR`

**Provided values** :

```
{
	"exception_object": EXCEPTION_OBJECT,
	"traceback": TRACEBACK,
}
```

- *EXCEPTION_OBJECT* (Type : class)

	The exception class object.

- *TRACEBACK* (Type : str)

	The full traceback of the exception as a string.

Note that more keys can be provided depending on the context :

```
{
	"client_socket": CLIENT_SOCKET,
	"client_instance": CLIENT_INSTANCE,
}
```

- *CLIENT_SOCKET* (Type : `socket.socket`)

  The raw client socket object.

- *CLIENT_INSTANCE* (Type : `ClientInstance`)

  The `ClientInstance` object representing the handled client.

---

```
@ServerInterface.on_malformed_request
```

Called when the server received a malformed request.

**Affiliated event constant** : `EVENT_MALFORMED_REQUEST`

**Provided values** :

```
{
	"client_instance": CLIENT_INSTANCE,
}
```

- *CLIENT_INSTANCE* (Type : `ClientInstance`)

  The `ClientInstance` object representing the handled client.

---

```
@ServerInterface.on_unhandled_verb
```

Called when the server has received a request containing an unhandled verb.

**Affiliated event constant** : `EVENT_UNHANDLED_VERB`

**Provided values** :

```
{
	"client_instance": CLIENT_INSTANCE,
}
```

- *CLIENT_INSTANCE* (Type : `ClientInstance`)

  The `ClientInstance` object representing the handled client.
