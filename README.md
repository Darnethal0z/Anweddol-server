# Anweddol-server

[![made-with-python](https://img.shields.io/badge/Made%20with-Python-important)](https://www.python.org/)
[![license](https://img.shields.io/badge/license-GPLv3-blue.svg)](https://shields.io/)
[![reddit](https://img.shields.io/reddit/subreddit-subscribers/Anweddol?style=social)](https://www.reddit.com/r/Anweddol/)

---

## Introduction

Anweddol is a client/server system providing temporary, SSH-controllable virtual machines to enhance anonymity online.

It’s usefulness comes when someone wants to use a fully functional computer while being exposed to less dangers by using it remotely on a dedicated server, and by destroying it after use.

## NOTE

This is the beta version, some bugs or malfunctions can occur during usage. 

## Content

This repository contains : 

- The Anweddol server core features source code ;
- The Anweddol server CLI implementation source code ;

To get the client source code, see the [Anweddol client repository](https://github.com/the-anweddol-project/Anweddol-client).

## Tech stack

The main technologies used are : 

- Python
- Libvirt
- SQLite3

But also : 

- [Cerberus](https://pypi.org/project/Cerberus/)
- [Cryptography](https://pypi.org/project/cryptography/)
- [Paramiko](https://pypi.org/project/paramiko/)
- [SQLAlchemy](https://www.sqlalchemy.org/)

## Installation

The Anweddol server installation requires a specific setup before installation and usage in order to provide a functional service.

See the [Administration guide](https://anweddol-server.readthedocs.io/en/latest/administration_guide/index.html) to learn more.

## Configuration

When the Anweddol server is installed, a YAML configuration file `/etc/anweddol/config.yaml` is created, containing all parameters used by the server to run. 

Before using it, the Anweddol server needs a specific setup to run. See the [Administration guide](https://anweddol-server.readthedocs.io/en/latest/administration_guide/index.html) to learn more.

## Documentation

You can retrieve the [Administration guide](https://anweddol-server.readthedocs.io/en/latest/administration_guide/index.html) on the readthedocs page.

See also the Anweddol server API references on the server [Developer documentation](https://anweddol-server.readthedocs.io/en/latest/developer_section/index.html) page.

## Bugs & New ideas

Anweddol is a community-driven project : You are free to bring new ideas, enhancement, report malfunctions or bugs, regardless of your competences.

Open a ticket on the [issue page](https://github.com/the-anweddol-project/Anweddol-server/issues) to do so.

## License

This software is under the GNU general public license v3, available under any later version.

This is free software: you are free to change and redistribute it. There is NO WARRANTY, to the extent permitted by law.

## Contact

See the Anweddol community pages : 

- Anweddol [reddit community page](https://www.reddit.com/r/Anweddol)
- Join the Anweddol [Zulip organization](https://anweddol.zulipchat.com)

## Developer / Maintainer

- Darnethal0z ([GitHub profile](https://github.com/Darnethal0z))

*Copyright 2023 The Anweddol project*
