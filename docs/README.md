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