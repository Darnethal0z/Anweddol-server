# Sanitization

---

## Request and response formatting

### Verify a request content

```{function} anwdlserver.core.sanitize.verifyRequestContent(request_dict)
```

Check if a request dictionary is a valid normalized [Request format](https://anweddol-server.readthedocs.io/en/latest/technical_specifications/core/communication.html#request-format).

**Parameters** :

> ```{attribute} request_dict
> Type : dict
> 
> The request dictionary to verify.
> ```

**Return value** : 

> Type : tuple
>
> A tuple representing the verification results :

> ```
> (
> 	True,
> 	sanitized_request_dictionary
> )
> ```

> if the `request_dict` is a valid normalized [Request format](https://anweddol-server.readthedocs.io/en/latest/technical_specifications/core/communication.html#request-format),

> ```
> (
> 	False,
> 	errors_dictionary
> )
> ```

> otherwise.

> - *sanitized_request_dictionary*
>	Type : dict
> 
>   The sanitized request as a normalized [Request format](../../../technical_specifications/core/communication.md) dictionary.
> 
> - *errors_dictionary*
>	Type : dict
> 
>   A dictionary depicting the errors detected in `request_dict` according to the [Cerberus](https://docs.python-cerberus.org/en/stable/errors.html) error format.

```{warning}
The function `verifyRequestContent()` does not use strict verification. It only checks if the required keys and values exist and are correct, but it is open to unknown keys or structures for the developer to be able to implement its own mechanisms (see the technical specifications [Sanitization section](../../../technical_specifications/core/communication.md) to learn more).
```

### Make a normalized response

```{function} anwdlserver.core.sanitize.makeResponse(success, message, data, reason)
```

Make a normalized response dictionary.

**Parameters** :

> ```{attribute} success
> Type : bool
> 
> `True` to announce a success, `False` otherwise.
> ```

> ```{attribute} message
> Type : str
> 
> The message to send.
> ```

> ```{attribute} data
> Type : dict
> 
>The data to send. The content must be an empty dict or a normalized [Response format](../../../technical_specifications/core/communication.md). Default is an empty dict.
> ```

> ```{attribute} reason
> Type : str
> 
> The reason to specify if `success` is set to `False`. The value will be appended to the message in the form : `Refused request (reason : <reason>)`. Default is `None`.
> ```

**Return value** : 

> Type : tuple
>
> A tuple representing a valid [Response format](../../../technical_specifications/core/communication.md) dictionary :

> ```
> (
> 	True,
> 	response_dictionary
> )
> ```

> if the operation succeeded,

> ```
> (
> 	False,
> 	errors_dictionary
> )
> ```
 
> otherwise.

> - *response_dictionary*
>	Type : dict
> 
>   The response dictionary as a normalized [Response format](../../../technical_specifications/core/communication.md).
> 
> - *errors_dictionary*
>	Type : dict
> 
>   A dictionary depicting the errors detected in parameters according to the [Cerberus](https://docs.python-cerberus.org/en/stable/errors.html) error format.

```{note}
The `sendResponse` method from `ClientInstance` wraps this function in its process.
```

```{warning}
Like `verifyRequestContent`, the method only checks if the required keys and values exist and are correct, but it is open to unknown keys or structures for the developer to be able to implement its own mechanisms.
```