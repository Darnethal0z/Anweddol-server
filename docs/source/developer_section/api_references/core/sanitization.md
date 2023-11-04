# Sanitization

---

## Request and response format

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
> 
> ```
> (
> 	is_request_format_valid,
> 	sanitized_request_dictionary,
>   errors_dictionary,
> )
> ```
> 
> - *is_request_format_valid*
>
>	Type : bool
> 
>   `True` if the request dictionary format is valid, `False` otherwise.
>
> - *sanitized_request_dictionary*
>
>	Type : dict | `NoneType`
> 
>   The sanitized request as a normalized [Request format](../../../technical_specifications/core/communication.md) dictionary. `None` if `is_request_format_valid` is set to `False`.
> 
> - *errors_dictionary*
>
>	Type : dict | `NoneType`
> 
>   A dictionary depicting the errors detected in `request_dict` according to the [Cerberus](https://docs.python-cerberus.org/en/stable/errors.html) error format. `None` if `is_request_format_valid` is set to `True`.

```{warning}
The function `verifyRequestContent` does not use strict verification. It only checks if the required keys and values exist and are correct, but it is open to unknown keys or structures for the developer to be able to implement its own mechanisms (see the technical specifications [Sanitization section](../../../technical_specifications/core/communication.md) to learn more).
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
> The data to send. The content must be an empty dictionary or a dictionary where some specific keys values must be compliant to the format specified in the technical specifications [Communication section](../../../technical_specifications/core/communication.md). Default is an empty dictionary.
> ```

> ```{attribute} reason
> Type : str | `NoneType`
> 
> The reason to specify if `success` is set to `False`. The value will be appended to the message in the form : `Refused request (reason : <reason>)`. Default is `None`.
> ```

**Return value** : 

> Type : tuple
>
> A tuple representing the verification results :

> ```
> (
> 	is_response_format_valid,
> 	sanitized_response_dictionary,
>   errors_dictionary,
> )
> ```

> - *is_response_format_valid*
>
>	Type : bool
> 
>   `True` if the response dictionary format is valid, `False` otherwise.
>
> - *sanitized_response_dictionary*
>
>	Type : dict | `NoneType`
> 
>   The sanitized response as a normalized [Response format](../../../technical_specifications/core/communication.md) dictionary. `None` if `is_response_format_valid` is set to `False`.
> 
> - *errors_dictionary*
>
>	Type : dict | `NoneType`
> 
>   A dictionary depicting the errors detected in `response_dict` according to the [Cerberus](https://docs.python-cerberus.org/en/stable/errors.html) error format. `None` if `is_response_format_valid` is set to `True`.

```{note}
The `sendResponse` method from `ClientInstance` wraps this function in its process.
```

```{warning}
Like `verifyRequestContent`, this function only checks if the required keys and values exist and are correct, but it is open to unknown keys or structures for the developer to be able to implement its own mechanisms.
```