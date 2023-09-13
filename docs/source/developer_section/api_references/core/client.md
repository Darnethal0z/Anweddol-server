# Client

---

## class *ClientInstance*

### Definition

```{class} anwdlserver.core.client.ClientInstance(socket, timeout, rsa_wrapper, aes_wrapper, exchange_keys)
```

This class is used when a new client has just connected to a listening socket, and when  RSA and AES keys must be exchanged in order to guarantee the security and integrity of request and response transmission.

```{tip}
This class can be used in a 'with' statement.
```

**Parameters** :

> ```{attribute} socket
> > Type : `socket.socket`
> 
> The client [socket descriptor](https://docs.python.org/3/library/socket.html#socket.socket). Must be an active client socket.
> ```

> ```{attribute} timeout
> > Type : int
> 
> The timeout to apply to the client. Default is `None`.
> ```

> ```{attribute} rsa_wrapper
> > Type : `RSAWrapper`
> 
> The `RSAWrapper` object that will be used with the client. Default is `None`.
> ```

> ```{attribute} aes_wrapper
> > Type : `AESWrapper`
> 
> The `AESWrapper` object that will be used with the client. Default is `None`.
> ```

> ```{warning}
> The `rsa_wrapper` remote public key and the `aes_wrapper` key will be set with those of the client if they are exchanged.
> ```

> ```{attribute} exchange_keys
> > Type : bool
> 
> Automatically exchange keys on initialization. Default is `True`.
> ```

> ```{note} 
> The method `closeConnection()` will be called on `__del__` method.
> ```

### General usage

```{classmethod} isClosed()
```

Check if the client socket is closed or not.

**Parameters** : 

> None.

**Return value** :

> `True` if the client socket is closed, `False` otherwise.

---

```{classmethod} getSocketDescriptor()
```

Get the client [socket descriptor](https://docs.python.org/3/library/socket.html#socket.socket).

**Parameters** : 

> None.

**Return value** : 

> The [socket descriptor](https://docs.python.org/3/library/socket.html#socket.socket) of the client.

---

```{classmethod} getIP()
```

Get the client IP.

**Parameters** : 

> None.

**Return value** : 

> The client IP, in a IPv4 format.

---

```{classmethod} getID()
```

Get the client ID.

**Parameters** : 

> None.

**Return value** : 

> The client ID. It is the first 7 characters of the client's IP SHA256 (see the administration guide [Logging section](../../../administration_guide/logging.md) to learn more).

---

```{classmethod} getCreationTimestamp()
```

Get the client creation timestamp.

**Parameters** : 

> None.

**Return value** : 

> The client creation timestamp.

---

```{classmethod} getStoredRequest()
```

Get the stored received request from the client.

**Parameters** : 

> None.

**Return value** : 

> A dictionary following the normalized [Request format](../../../technical_specifications/core/communication.md), or `None` if there is none.

---

```{classmethod} getRSAWrapper()
```

Get the client `RSAWrapper` object.

**Parameters** : 

> None.

**Return value** : 

> The `RSAWrapper` object of the client.

---

```{classmethod} getAESWrapper()
```

Get the client `AESWrapper` object.

**Parameters** : 

> None.

**Return value** : 

> The `AESWrapper` object of the client.

---

```{classmethod} setRSAWrapper(rsa_wrapper)
```

Set the client `RSAWrapper` object.

**Parameters** :

> ```{attribute} rsa_wrapper
> > Type : `RSAWrapper`
> 
> The `RSAWrapper` object to set.
> ```

**Return value** : 

> `None`.

---

```{classmethod} setAESWrapper(aes_wrapper)
```

Set the client `AESWrapper` object.

**Parameters** :

> ```{attribute} aes_wrapper
> > Type : `AESWrapper`
> 
> The `AESWrapper` object to set.
> ```

**Return value** : 

> `None`.

---

```{classmethod} closeConnection()
```

Close the client connection.

**Parameters** : 

> None.

**Return value** : 

> `None`.

**Possible raise classes** :

> ```{exception} RuntimeError
> An error occured due to a failed internal action.
>
> Raised in this method if the client is already closed.
> ```

### Key transmission

```{classmethod} exchangeKeys(receive_first)
```

Exchange the local RSA and AES keys with the client.

**Parameters** :

> ```{attribute} receive_first
> > Type : bool
> 
> `True` to receive the key first, `False` otherwise. Default is `True`.
> ```

**Return value** : 

`None`.

**Possible raise classes** :

> ```{exception} RuntimeError
> An error occured due to a failed internal action.
> 
> Raised in this method if the client is closed.
> ```

```{note}
This method is just a wrapper exchanging RSA and AES keys using every related method below.
```

---

```{classmethod} sendPublicRSAKey()
```

Send the local public RSA key to the client.

**Parameters** : 

> None.

**Return value** : 

> `None`.

**Possible raise classes** :

> ```{exception} RuntimeError
> An error occured due to a failed internal action.
> 
> Raised in this method if the client is closed, or that the client refused the sent packet or the RSA key.
> ```
---

```{classmethod} recvPublicRSAKey()
```

Receive the client public RSA key from the client.

**Parameters** : 

> None.

**Return value** : 

> `None`.

**Possible raise classes** :

> ```{exception} ValueError
> An error occured due to an invalid value set before or during the method call.
> 
> Raised in this method if an invalid key length has been received from the client.
> ```

> ```{exception} RuntimeError
> An error occured due to a failed internal action.
> 
> Raised in this method if the client is closed.
> ```

---

```{classmethod} sendAESKey()
```

Send the local AES key to the client.

**Parameters** : 

> None.

**Return value** : 

> `None`.

**Possible raise classes** :
  
> ```{exception} RuntimeError
> An error occured due to a failed internal action.
> 
> Raised in this method if the client is closed, or that the client refused the RSA key.
> ```

---

```{classmethod} recvAESKey()
```

Receive the AES key from the client.

**Parameters** : 

> None.

**Return value** : 

> `None`.

**Possible raise classes** :
  
> ```{exception} RuntimeError
> An error occured due to a failed internal action.
> 
> Raised in this method if the client is closed, or that the client refused the RSA key.
> ```

### Request and reponse

```{classmethod} sendResponse(success, message, data, reason)
```

Send a response to the client.

**Parameters** :

> ```{attribute} success
> > Type : bool
> 
> `True` to announce a success in the previous request processing, `False` otherwise.
> ```

> ```{attribute} message
> > Type : str
> 
> The message to send back to the client explaining the stata of the request processing.
> 
> Some pre-defined messages constants exists on the `anwdlserver.core.client` module :
> ```

>> ```{attribute} RESPONSE_MSG_OK
>> Message meaning that the request was processed withour errors.
>> ```

>> ```{attribute} RESPONSE_MSG_BAD_AUTH
>> Message meaning that an authentication procesus failed.
>> ```

>> ```{attribute} RESPONSE_MSG_BAD_REQ
>> Message meaning that an invalid request was received.
>> ```

>> ```{attribute} RESPONSE_MSG_REFUSED_REQ
>> Message meaning that the request was refused.
>> ```

>> ```{attribute} RESPONSE_MSG_UNAVAILABLE
>> Message meaning that the server is temporarily unavailable.
>> ```
  
>> ```{attribute} RESPONSE_MSG_INTERNAL_ERROR
>> Message meaning that an internal error occured during request processing.
>> ```

> ```{attribute} data
> > Type : dict
> 
> The data to send. Must be an empty dictionary or a normalized [Response format](../../../technical_specifications/core/communication.md) dictionary. Default is an empty dict.
> ```

> ```{attribute} reason
> > Type : str
> 
> An additional explanation concerning the response content. The value will be appended to the `message` value in the form : `Refused request (reason : <reason>)`, unless the passed value is `None`. Default is `None`.
> ```

**Return value** : 

> `None`.

**Possible raise classes** :

> ```{exception} ValueError
> An error occured due to an invalid value set before or during the method call.
> 
> Raised in this method if an invalid packet length has been received from the client.
> ```

> ```{exception} RuntimeError
> An error occured due to a failed internal action.
> 
> Raised in this method if the client is closed, or that the client refused the sent packet or the RSA key.
> ```

---

```{classmethod} recvRequest(store_request)
```

Receive a request from the client.

**Parameters** :

> ```{attribute} store_request
> > Type : bool
> 
> `True` to store the received request on the instance, `False` otherwise. Default is `True`.
> ```

**Return value** :

> The received request as a normalized [Request format](https://anweddol-server.readthedocs.io/en/latest/technical_specifications/core/communication.html#request-format) dictionary

**Possible raise classes** :

> ```{exception} ValueError
> An error occured due to an invalid value set before or during the method call.
> 
> Raised in this method if an invalid packet length has been received from the client.
> ```
  
> ```{exception} RuntimeError
> An error occured due to a failed internal action.
> 
> Raised in this method if the client is closed.
> ```