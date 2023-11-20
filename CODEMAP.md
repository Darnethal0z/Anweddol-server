# Code map

---

This file contains the source code files / folders mapping, with their respective descriptions.

> It is made for development guiding purposes.

## Source code tree

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

### `anwdlserver` root files

- `cli.py`

  This module contains the 'anwdlserver' CLI.

- `config.py`

  This module provides the 'anwdlserver' CLI with configuration file management features.
  
- `logging.py`

  This module provides the 'anwdlserver' CLI server process with logging features.
  
- `process.py`

  This module defines the 'anwdlserver' CLI server process.

- `utilities.py`

  This module provides some miscellaneous features that the 'anwdlserver' CLI various modules uses in their processes.

### `anwdlserver` `core` folder content

- `client.py`

  This module provides the Anweddol server with client representation and management features.

  It includes RSA / AES key exchange and Request / response processing.

- `crypto.py`

  This module provides the Anweddol server with RSA/AES encryption features.

  There is 2 provided encryption algorithms : RSA 4096 and AES 256 CBC.

- `database.py`

  This module provides the Anweddol server with database features.

  It is based on a SQLAlchemy memory database instance, since it is used for run time credentials storage only.

- `port_forwarding.py`

  This module provides the Anweddol server with port forwarding features.

  It is used to allow clients and container domains to communicate.

- `sanitization.py`

  This module provides the Anweddol server with normalized request / response values and formats 
  verification features.

- `server.py`

  This module is the main Anweddol server process.

  It connects every other core modules into a single one so that they can all be used in a single module.

- `utilities.py`

  This module contains miscellaneous features useful for the server.

- `virtualization.py`

  This module provides the Anweddol server with virtualization appliance and container management 
  features.

  It is based on the libvirt API.

### `anwdlserver` `tools` folder content

- `access_token.py`

  This file provides additional features for access token storage and management. 

  Its primary goal is to provide an authentication method that can be implemented for server usage / access restriction. If the server is in a public or multi-user area, it makes a pretty easy-to-deploy solution to authenticate users.

### `anwdlserver` `web` folder content

- `server.py`

  This file contains an HTTP alternative to the classic server.

  It consists of a REST API based on the ServerInterface class, which provides all the features of a classic server, but in the form of a web server.