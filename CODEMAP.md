# Code map

---

This file contains the code source files / folders mapping, with their respective descriptions.

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

## `anwdlserver` CLI root files

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

## `anwdlserver` `core` folder content

- `client.py` :
- `crypto.py` : 
- `database.py` : .
- `port_forwarding.py` :
- `sanitization.py` :
- `server.py` :
- `utilities.py` : 
- `virtualization.py` : 

## `anwdlserver` `tools` folder content

- `access_token.py`

  This file provides additional features for access token storage and management. 

## `anwdlserver` `web` folder content

- `server.py`

  This file contains an HTTP alternative to the classic server.