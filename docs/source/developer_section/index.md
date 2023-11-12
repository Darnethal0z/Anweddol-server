# Developer section

----

Hello and welcome to the Anweddol server developer documentation.

Here, you'll find every informations and documentation about the [python](https://www.python.org/) server API features.

```{note}
At the root of `anwdlserver`, there is the CLI source code : They are not meant to be used on an external program.
```

## Before getting started

The Anweddol server installation requires a specific setup before installation and usage in order to provide a functional service.

See the administration guide [Installation section](../administration_guide/installation.md) before getting started on the server API.

```{note}
The "**Possible raise classes**" sections define exceptions specific to the method in question: others are likely to be raised.
```

## Examples

See basic server stubs that can be used as examples.

### `core` examples

```{toctree}
---
maxdepth: 3
includehidden:
---

examples/core/basic_server
```

```{toctree}
---
maxdepth: 3
includehidden:
---

examples/core/custom_verb_handle
```

```{toctree}
---
maxdepth: 3
includehidden:
---

examples/core/ip_filtering
```

```{toctree}
---
maxdepth: 3
includehidden:
---

examples/core/custom_container_capacity
```

### `web` examples

```{toctree}
---
maxdepth: 3
includehidden:
---

examples/web/basic_web_server
```

```{toctree}
---
maxdepth: 3
includehidden:
---

examples/web/basic_web_server_ssl
```

## API references

Learn about every features that the Anweddol server can provide.

### Core features

The core features, also called `core`, are every basic functionnalities that an Anweddol server must have in order to provide a valid service. 

The `ServerInterface` class is the main server which encompasses all these features into a single and easy-to-use object : 

```{toctree}
---
maxdepth: 3
includehidden:
---

api_references/core/server
```

If you want to make a more complex use of Anweddol, you can retrieve every others `core` features documentations and references below : 

```{toctree}
---
maxdepth: 3
includehidden:
---

api_references/core/client
```

```{toctree}
---
maxdepth: 3
includehidden:
---

api_references/core/cryptography
```

```{toctree}
---
maxdepth: 3
includehidden:
---

api_references/core/database
```

```{toctree}
---
maxdepth: 3
includehidden:
---

api_references/core/port_forwarding
```

```{toctree}
---
maxdepth: 3
includehidden:
---

api_references/core/sanitization
```

```{toctree}
---
maxdepth: 3
includehidden:
---

api_references/core/utilities
```

```{toctree}
---
maxdepth: 3
includehidden:
---

api_references/core/virtualization
```

### Tools features

The `tools` features are additional functionnalities (authentication utilities, ...) coming with the Anweddol server package.

These are not essential features, although they can be used in specific contexts : 

```{toctree}
---
maxdepth: 3
includehidden:
---

api_references/tools/access_token
```

### Web features

The `web` features consists of a REST API based on the `core` features, which provides all the features of a classic server, but in the form of a web server.

These are not essential features, although they can be used in specific contexts :

```{toctree}
---
maxdepth: 3
includehidden:
---

api_references/web/server
```

## CLI references

The actual Anweddol server CLI provides a JSON output feature that allows inter-program communication.

You may retrieve every references concerning the JSON format and keys : 

```{toctree}
---
maxdepth: 3
includehidden:
---

cli/json_output
```

## Troubleshooting

A troubleshooting page is also available for the Anweddol server API : 

```{toctree}
---
maxdepth: 3
includehidden:
---

troubleshooting
```