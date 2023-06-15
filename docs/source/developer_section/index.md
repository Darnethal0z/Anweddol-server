# Developer section

----

Hello and welcome to the Anweddol server developer documentation.

Here, you'll find every informations and documentation about the server [python](https://www.python.org/) API features.

**NOTE** : At the root of `anwdlserver`, there is the CLI source code : They are not meant to be used on an external program since it's the server implementation's code itself.

## Important note

The Anweddol server installation requires a specific setup before installation and usage in order to provide a functional service.

See the administration guide [Installation section](https://anweddol-server.readthedocs.io/en/latest/administration_guide/installation.html) to learn more before getting started on the server API.

## Examples

See basic server stubs that can be used as examples.

```{toctree}
---
maxdepth: 3
includehidden:
---

examples/basic_server
```

```{toctree}
---
maxdepth: 3
includehidden:
---

examples/custom_verb_handle
```

```{toctree}
---
maxdepth: 3
includehidden:
---

examples/ip_filtering
```

```{toctree}
---
maxdepth: 3
includehidden:
---

examples/custom_container_capacity
```

## API references

Learn about every features that the Anweddol server can provide.
You can also see the *Technical specificatons* section to get every informations on how the Anweddol server works.

### Core features

The core features, also called `core`, are every needed functionnalities that an Anweddol server must have in order to provide a valid service.

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

api_references/core/sanitization
```

```{toctree}
---
maxdepth: 3
includehidden:
---

api_references/core/server
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

```{toctree}
---
maxdepth: 3
includehidden:
---

api_references/tools/accesstk
```

## CLI references

The actual Anweddol server CLI provides a JSON output feature that allows inter-program communication.

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