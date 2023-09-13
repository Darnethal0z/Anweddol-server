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
$ pip install --upgrade myst-parser
```

**NOTE** : By default, the `sphinx_rtd_theme` theme is used on the `conf.py` file in the sources. If you want to use it, install it with pip :

```
$ pip install sphinx_rtd_theme
```

## Build the documentation

Execute the Makefile to build the documentation depending of your need : 

```
$ make <target>
```

## ReadTheDocs integration notice

If you want to publish this documentation on ReadTheDocs, every needed dependancies are already specified in the `requirements.txt` file in the sources.