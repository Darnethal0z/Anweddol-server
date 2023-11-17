# Code map

---

This file contains the code tree mapping, with every python files and their respectives description.

> It is made for development guiding purposes.

```
anwdlserver
├── cli.py
├── config.py
├── logging.py
├── process.py
├── utilities.py
├── core
│   ├── client.py
│   ├── crypto.py
│   ├── database.py
│   ├── port_forwarding.py
│   ├── sanitization.py
│   ├── server.py
│   ├── utilities.py
│   └── virtualization.py
├── tools
│   └── access_token.py
└── web
    └── server.py
```

## `anwdlserver` CLI files

- `cli.py` : This file contains the main CLI source code, permits interaction with Anweddol server environment and lifecycle control.
- `config.py` : This file provides the main CLI with configuration file loading and verification features.
- `logging.py` : This file contains every logging features used by the Anweddol server CLI process.
- `process.py` : This file is the main Anweddol server process provided by the CLI : It uses every `core`, `tools` and `web` features.
- `utilities.py` : This file contains miscellaneous features used by the main Anweddol server process and the main CLI.

## `anwdlserver` `core` files (in the `core` folder)

- `client.py` : This file provides the Anweddol server with client representation and management features.
- `crypto.py` : This file provides the Anweddol server with RSA/AES encryption features.
- `database.py` : This file provides the Anweddol server with database features.
- `port_forwarding.py` : This file provides the Anweddol server with port forwarding features.
- `sanitization.py` : This file provides the Anweddol server with port forwarding features.
- `server.py` : This file is the main Anweddol server process.
- `utilities.py` : This file contains miscellaneous features useful for the server.
- `virtualization.py` : This file provides the Anweddol server with virtualization appliance and container management features.

## `anwdlserver` `tools` files (in the `tools` folder)

- `access_token.py` : This file provides additional features for access token storage and management. 

## `anwdlserver` `web` files (in the `web` folder)

- `server.py` : This file contains an HTTP alternative to the classic server.