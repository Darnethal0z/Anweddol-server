# The Anweddol server

[![made-with-python](https://img.shields.io/badge/Made%20with-Python-important)](https://www.python.org/)
[![build-passing](https://img.shields.io/badge/build-passing-green.svg)](https://shields.io/)
[![license](https://img.shields.io/badge/license-GPLv3-blue.svg)](https://shields.io/)
[![reddit](https://img.shields.io/reddit/subreddit-subscribers/Anweddol?style=social)](https://www.reddit.com/r/Anweddol/)

----

## Global overview

Anweddol is a client/server system providing temporary, SSH-controllable virtual machines to enhance anonymity online.

It’s usefulness comes when someone wants to use a fully functional computer while being exposed to less dangers by using it remotely on a dedicated server, and by destroying it after use.

## Effective scenario

*terminology :*

- **Container** : A temporary virtual machine hosted on a server that can be controlled from the client side. 

1. Alice wants to have access to a container. She will first send a request asking it to create a new container.
2. The server will start a new container, administer it and send the SSH credentials to Alice for her to be able to securely interact with the container.
3. Once that Alice is done, she will send another request with previously received container identification and credentials to the server.
4. The server identifies the affiliated running container, and destroys it.

## Contents

```{toctree}
---
maxdepth: 3
includehidden:
---

administration_guide/index
```

```{toctree}
---
maxdepth: 3
includehidden:
---

developer_section/index
```

```{toctree}
---
maxdepth: 2
includehidden:
---

technical_specifications/index
```

## Contribution

See the contribution section to know how to contribute : 

```{toctree}
---
maxdepth: 3
includehidden:
---

contribute
```

## Links

Here is the social links of the Anweddol project : 

- [https://www.reddit.com/r/Anweddol/](https://www.reddit.com/r/Anweddol/)
- [https://github.com/the-anweddol-project](https://github.com/the-anweddol-project)
- [https://anweddol.zulipchat.com](https://anweddol.zulipchat.com)

You can also mail `the-anweddol-project@proton.me`, consider using the [PGP public key](https://the-anweddol-project.github.io/contact/A050C2B36F2E80BE6FDE6E0F0D3F21975020EFC0.asc)

## Indices and tables

- {ref}`genindex`
- {ref}`search`