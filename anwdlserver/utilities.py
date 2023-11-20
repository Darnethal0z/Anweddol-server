"""
Copyright 2023 The Anweddol project
See the LICENSE file for licensing informations
---

This module provides some miscellaneous features that the 'anwdlserver' CLI
various modules uses in their processes.

NOTE : Some functions be hard to debug with the several except statements,
please considerate this function when implementing a new experimental feature

"""

import os


class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"


def createFileRecursively(path, is_folder=False):
    try:
        os.makedirs(os.path.dirname(path) if not is_folder else path)

    except FileExistsError:
        pass

    if is_folder:
        return

    with open(path, "w") as fd:
        fd.close()
