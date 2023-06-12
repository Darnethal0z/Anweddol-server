# Sanitization

---

> Normalized request / response values and formats

> Package `anwdlserver.core.sanitize`

## Constants

None

## Functions

```
verifyRequestContent(request_dict: dict) -> tuple
```

> Check if a request dictionary is a valid normalized [Request format](https://anweddol-server.readthedocs.io/en/latest/technical_specifications/core/communication.html#request-format)

_Parameters_ :

- `request_dict` : The request dictionary

_Return value_ :

- A tuple representing the verification results :

```
(
	True,
	sanitized_request_dictionary
)
```

if the `request_dict` is a valid normalized [Request format](https://anweddol-server.readthedocs.io/en/latest/technical_specifications/core/communication.html#request-format),

```
(
	False,
	errors_dictionary
)
```

otherwise.

- `sanitized_request_dictionary` : The sanitized request as a normalized [Request format](https://anweddol-server.readthedocs.io/en/latest/technical_specifications/core/communication.html#request-format) dictionary.
- `errors_dictionary` : A dictionary depicting the errors detected in `request_dict` according to the [Cerberus](https://docs.python-cerberus.org/en/stable/errors.html) error format.

**NOTE** : The function `verifyRequestContent` does not use strict verification. It only checks if the required keys and values exist and are correct, but it is open to unknown keys or structures for the developer to be able to implement its own mechanisms (see the technical specifications [Sanitization section](https://anweddol-server.readthedocs.io/en/latest/technical_specifications/core/communication.html#sanitization) to learn more).

---

```
makeResponse(
    success: bool,
    message: str,
    data: dict = {},
    reason: str = None
) -> tuple:
```

> Make a normalized response dictionary

_Parameters_ :

- `success` : `True` to announce a success, `False` otherwise
- `message` : The message to send
- `data` : The data to send. The content must be an empty dict or a normalized [Response format](https://anweddol-server.readthedocs.io/en/latest/technical_specifications/core/communication.html#response-format).
- `reason` : The reason to specify if `success` is set to `False`. The value will be appended to the message like : `Refused request (reason : <specified_reason>)`

_Return value_ :

- A tuple representing a valid [Response format](https://anweddol-server.readthedocs.io/en/latest/technical_specifications/core/communication.html#response-format) dictionary :

```
(
	True,
	response_dictionary
)
```

if the operation succeeded,

```
(
	False,
	errors_dictionary
)
```

otherwise.

- `response_dictionary` : The response dictionary as a normalized [Response format](https://anweddol-server.readthedocs.io/en/latest/technical_specifications/core/communication.html#response-format).
- `errors_dictionary` : A dictionary depicting the errors detected in parameters according to the [Cerberus](https://docs.python-cerberus.org/en/stable/errors.html) error format.

**NOTE** : The `sendResponse` method from `ClientInstance` wraps this function in its process. Like `verifyRequestContent`, the method only checks if the required keys and values exist and are correct, but it is open to unknown keys or structures for the developer to be able to implement its own mechanisms.
