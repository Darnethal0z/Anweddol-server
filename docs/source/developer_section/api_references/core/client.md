# Client

---

> Client management features

> Package `anwdlserver.core.client`

## Constants

Default values :

| Name                         | Value  | Description                                  |
| ---------------------------- | ------ | -------------------------------------------- |
| `DEFAULT_STORE_REQUEST`      | `True` | Store the request in the instance by default |
| `DEFAULT_AUTO_EXCHANGE_KEYS` | `True` | Exchange keys on connection by default       |
| `DEFAULT_RECEIVE_FIRST`      | `True` | Receive the public key first by default      |

Constants definition :

| Name          | Value | Definition                                                                 |
| ------------- | ----- | -------------------------------------------------------------------------- |
| `MESSAGE_OK`  | `"1"` | Message used during key exchange to transmit a state or an acknowledgement |
| `MESSAGE_NOK` | `"0"` | Message used during key exchange to transmit a state or an acknowledgement |

## Classes

### `ClientInstance`

#### Definition

```
class ClientInstance(
	socket: socket.socket,
	timeout: int = None,
	rsa_wrapper: RSAWrapper = None,
	aes_wrapper: AESWrapper = None,
	auto_exchange_key: bool = DEFAULT_AUTO_EXCHANGE_KEYS,
)
```

> Represents a connected client

_Parameters_ :

- `socket` : The client socket descriptor. Must be a connected active client socket
- `timeout` : The timeout to apply to the client
- `rsa_wrapper` : The `RSAWrapper` instance that will be used on the client
- `aes_wrapper` : The `AESWrapper` instance that will be used on the client
- `auto_exchange_key` : Automatically exchange keys on initialization

**NOTE** : The client socket will be automatically closed on `__del__` method. The parameter `socket` must be a valid open socket descriptor representing a client connection.

#### Methods

```
isClosed() -> bool
```

> Check if the client is closed

_Parameters_ :

- None

_Return value_ :

- `True` if the server is closed, `False` otherwise

---

```
getSocketDescriptor() -> socket.socket
```

> Get the client socket descriptor

_Parameters_ :

- None

_Return value_ :

- The socket descriptor of the client

---

```
getIP() -> str
```

> Get the client IP

_Parameters_ :

- None

_Return value_ :

- The client IP as an IPv4 string

---

```
getID() -> str
```

> Get the client ID

_Parameters_ :

- None

_Return value_ :

- The client ID. It is the first 7 characters of the client's IP SHA256 (see the administration guide [Logging section](https://anweddol-server.readthedocs.io/en/latest/administration_guide/logging.html) to learn more).

---

```
getTimestamp() -> int
```

> Get the client creation timestamp

_Parameters_ :

- None

_Return value_:

- The creation timestamp

---

```
getStoredRequest() -> None | dict
```

> Get the stored request

_Parameters_ :

- None

_Return value_ :

- A dictionary following the normalized [Request format](https://anweddol-server.readthedocs.io/en/latest/technical_specifications/core/communication.html#request-format) or `None` if there is none

---

```
getRSAWrapper() -> RSAWrapper
```

> Get the client `RSAWrapper` instance

_Parameters_ :

- None

_Return value_:

- The `RSAWrapper` instance of the client

---

```
getAESWrapper() -> AESWrapper
```

> Get the client `AESWrapper` instance

_Parameters_ :

- None

_Return value_:

- The `AESWrapper` instance of the client

---

```
setRSAWrapper(rsa_wrapper: RSAWrapper) -> None
```

> Set the client `RSAWrapper` instance

_Parameters_ :

- `rsa_wrapper` : The `RSAWrapper` instance to set

_Return value_ :

- None

---

```
setAESWrapper(aes_wrapper: AESWrapper) -> None
```

> Set the client `AESWrapper` instance

_Parameters_ :

- `aes_wrapper` : The `AESWrapper` instance to set

_Return value_ :

- None

---

```
sendPublicRSAKey() -> None
```

> Send the local public RSA key

_Parameters_ :

- None

_Return value_ :

- None

_Possible raise classes_ :

- `RuntimeError`

_Possible raise classes_ : 

- `RuntimeError`

---

```
recvPublicRSAKey() -> None
```

> Receive the client public RSA key

_Parameters_ :

- None

_Return value_ :

- None

_Possible raise classes_ :

- `ValueError`
- `RuntimeError`

---

```
sendAESKey() -> None
```

> Send the local AES key

_Parameters_ :

- None

_Return value_ :

- None

_Possible raise classes_ :

- `ValueError`
- `RuntimeError`

---

```
recvAESKey() -> None
```

> Receive the local AES key

_Parameters_ :

- None

_Return value_ :

- None

_Possible raise classes_ :

- `ValueError`
- `RuntimeError`

---

```
exchangeKeys(receive_first: bool = DEFAULT_RECEIVE_FIRST) -> None
```

> Exchange the local RSA and AES keys with the client

_Parameters_ :

- `receive_first` : `True` to receive the public key first, `False` otherwise

_Return value_ :

- None

_Possible raise classes_ :

- `ValueError`
- `RuntimeError`

---

```
sendResponse(
	success: bool,
	message: str,
	data: dict = {},
	reason: str = None
) -> None
```

> Send a response to the client

_Parameters_ :

- `success` : `True` to announce a success, `False` otherwise
- `message` : The message to send
- `data` : The data to send. The content must be an empty dictionary or a normalized [Response format](https://anweddol-server.readthedocs.io/en/latest/technical_specifications/core/communication.html#response-format) dictionary.
- `reason` : The reason to specify if `success` is set to `False`. The value will be appended to the message like : `Refused request (reason : <specified_reason>)`

_Return value_ :

- None

_Possible raise classes_ :

- `ValueError`
- `RuntimeError`

---

```
recvRequest(store_request: bool = DEFAULT_STORE_REQUEST) -> tuple
```

> Receive a request from the client

_Parameters_ :

- `store_request` : Store the received request on instance or not

_Return value_ :

- The received request as a normalized [Request format](https://anweddol-server.readthedocs.io/en/latest/technical_specifications/core/communication.html#request-format) dictionary

_Possible raise classes_ :

- `ValueError`
- `RuntimeError`

---

```
closeConnection() -> None
```

> Close the client connection

_Parameters_ :

- None

_Return value_ :

- None

**NOTE** : This method is automatically called within the `__del__` method, but it is programatically better to call it naturally

_Possible raise classes_ :

- `RuntimeError`
