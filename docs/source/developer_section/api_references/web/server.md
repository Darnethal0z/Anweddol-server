# Web server

---

## Constants

In the module `anwdlserver.web.server` : 

### Default values

Constant name                       | Value   | Definition
----------------------------------- | ------- | ----------
*DEFAULT_RESTWEBSERVER_LISTEN_PORT* | 8080    | The default web server listen port.
*DEFAULT_ENABLE_SSL*                | `False` | Enable SSL support by default or not.

## class *RESTWebServerInterface*

### Definition

```{class} anwdlserver.web.server.WebServerInterface(runtime_container_iso_file_path, listen_port, runtime_virtualization_interface, runtime_database_interface, runtime_port_forwarding_interface, enable_ssl, ssl_pem_private_key_file_path, ssl_pem_certificate_file_path)
```

This class is the HTTP alternative to the classic `core` server. It consists of a REST API based on the `ServerInterface` class, which provides all the features of a classic server, but in the form of a web server.

The request / response scheme stays the same, except that they are exprimed in the form of an URL : "http(s)://server:port/verb". The server will respond by a JSON-formatted normalized [response dictionary](../../../technical_specifications/core/communication.md).

**Parameters** :

> ```{attribute} runtime_container_iso_file_path
> Type : str
> 
> The container ISO file path that will be used for containers.
> ```

> ```{attribute} listen_port
> Type : int
> 
> The listen port that the web server will be using. Default is `8080`.
> ```

> ```{attribute} runtime_virtualization_interface
> Type : `VirtualizationInterface`
> 
> The `VirtualizationInterface` object that will be used by the server, or `None` to let > the server generate one. Default is `None`.
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

> ```{attribute} enable_ssl
> Type : bool
> 
> `True` to enable SSL support, `False` otherwise. Default is `False`.
> ```

> ```{attribute} ssl_pem_private_key_file_path
> Type : str
> 
> The SSL private key file path, in PEM format. Default is `None`.
> ```

> ```{attribute} ssl_pem_certificate_file_path
> Type : str
> 
> The SSL certificate file path, in PEM format. Default is `None`.
> ```

```{tip}
If you need a private key and a certificate, you can generate them with `openssl` :

`$ openssl req -newkey rsa:4096 -nodes -keyout private_key.pem -x509 -days 365 -out certificate.pem`

This command generates a 4096-bit private key and a self-signed certificate. Answer the questions and set the `ssl_pem_private_key_file_path` parameter with the `private_key.pem` file path, and the `ssl_pem_certificate_file_path` parameter with the `certificate.pem` file path.

([source](https://www.digitalocean.com/community/tutorials/openssl-essentials-working-with-ssl-certificates-private-keys-and-csrs))
```

```{note} 
The container ISO path must point to a valid [ISO image](../../../administration_guide/container_iso.md).
```

```{warning}
This class inherits of every `ServerInterface` classes attributes.

Every other classes listed below this point is part of this class, but can be combined with `ServerInterface` methods as well.

If the parameter `enable_ssl` is set to `True`, the parameters `ssl_pem_private_key_file_path` and `ssl_pem_certificate_file_path` must be set.
```

### Manual handler execution

```{classmethod} executeRequestHandler(verb, request)
```

Execute an HTTP request handler.

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

> ```{attribute} request
> Type : [`twisted.web.http.Request`](https://docs.twisted.org/en/stable/api/twisted.web.http.Request.html)
> 
> The [`twisted.web.http.Request`](https://docs.twisted.org/en/stable/api/twisted.web.http.Request.html) object representing the request to handle. Default is `None`.
> ```

**Return value** : 

> Type : dict
>
> A response dictionary as a normalized [Response format](../../../technical_specifications/core/communication.md).

```{note}
This method is a redefinition of the `ServerInterface` `executeRequestHandler` method.
```

### Events handling

Since the client system changes for this class, some of the initials event decorators behaviours from `ServerInterface` was modified.

```{warning}
Note that every others event handlers passing `ClientInstance` objects in the `data` parameter will be set to `None`. In addition to this, the [`twisted.web.http.Request`](https://docs.twisted.org/en/stable/api/twisted.web.http.Request.html) object and the request verb will be passed instead, as `request` and `verb` parameters respectively.
```

#### Modified decorators references

```{note}
The `RESTWebServerInterface` class initializes its inherited `ServerInterface` class with the `passive_mode` parameter set to `True`, meaning that every client instances specified in event handler `data` parameters when called will be set to `None`.
```

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
	"verb": VERB,
	"request": REQUEST
}
```

- *VERB*

  Type : str

  The request verb.

- *REQUEST*

  Type : [`twisted.web.http.Request`](https://docs.twisted.org/en/stable/api/twisted.web.http.Request.html)

  The [`twisted.web.http.Request`](https://docs.twisted.org/en/stable/api/twisted.web.http.Request.html) object depicting the received request.

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
	"traceback": TRACEBACK,
}
```

- *TRACEBACK*

  Type : str

  The full traceback of the exception as a string.

Note that more keys can be provided depending on the context :

```
{
	"request": REQUEST,
}
```

- *REQUEST*

  Type : [`twisted.web.http.Request`](https://docs.twisted.org/en/stable/api/twisted.web.http.Request.html)

  The [`twisted.web.http.Request`](https://docs.twisted.org/en/stable/api/twisted.web.http.Request.html) object depicting the received request.

#### Unused decorators list

There decorators below will not be used during `RESTWebServerInterface` run time :

- `@ServerInterface.on_client_initialized`
- `@ServerInterface.on_client_closed`
- `@ServerInterface.on_connection_accepted`

### Undocumented methods

- `_extract_post_request_args_values(request_args)`
- `_handle_error(exception_object=None, event=EVENT_RUNTIME_ERROR, message=RESPONSE_MSG_INTERNAL_ERROR, data={})`
- `_handle_home_from_http(request)`
- `_handle_stat_request_from_http(request)`
- `_handle_create_request_from_http(request)`
- `_handle_destroy_request_from_http(request)`
- `_handle_http_request(request)`
- `_create_deferred_http_request_handle(request)`
- `_start_server()`
- `_stop_server(die_on_error=False)`
- `render_POST(request)`
- `render_GET(request)`