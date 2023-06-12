# Anweddol server documentation source code

---

This folder container the Anweddol server documentation source code.

The documentation is build with [sphinx](https://www.sphinx-doc.org/).

## Prerequisites

Sphinx must be installed. Execute : 

```
$ pip install sphinx 
```

And install the `myst` plugin for markdown support : 

```
pip install --upgrade myst-parser
```

## Build the documentation

Execute the Makefile to build the documentation depending of your need : 

```
make <target>
```

**NOTE** : Man pages are already pre-built. To install them on your Linux system, copy the `build/man/anwdlserver.1` file on `/usr/local/share/man/man1/`, and reload the man database by executing : 

```
sudo mandb
```