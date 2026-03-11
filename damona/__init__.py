#
#  This file is part of Damona software
#
#  Copyright (c) 2020-2021 - Damona Development Team
#
#  File author(s):
#      Thomas Cokelaer <thomas.cokelaer@pasteur.fr>
#
#  Distributed under the terms of the 3-clause BSD license.
#  The full license is in the LICENSE file, distributed with this software.
#
#  website: https://github.com/cokelaer/damona
#  documentation: http://damona.readthedocs.io
#
##############################################################################
"""Damona – Singularity-based reproducible environment manager.

Damona provides a command-line tool and Python API for managing collections of
`Singularity <https://sylabs.io/singularity/>`_ containers as reproducible
software environments.  It mirrors the *activate / deactivate* workflow of
conda but relies exclusively on Singularity images so that executables are
always bit-for-bit identical across machines.

Key public symbols re-exported from sub-modules:

* :class:`~damona.common.Damona` – top-level manager
* :class:`~damona.environ.Environ` – environment collection manager
* :class:`~damona.environ.Environment` – single named environment
* :class:`~damona.registry.Registry` – software registry
"""
import importlib.metadata as metadata
import os
import sys

import colorlog


def get_package_version(package_name):
    """Return the installed version string of *package_name*.

    Uses :mod:`importlib.metadata` to look up the distribution version.  If
    the package is not installed a descriptive placeholder string is returned
    instead of raising an exception.

    :param str package_name: The distribution name (e.g. ``"damona"``).
    :returns: Version string such as ``"1.2.3"``, or
        ``"<package_name> not found"`` when not installed.
    :rtype: str
    """
    try:
        version = metadata.version(package_name)
        return version
    except metadata.PackageNotFoundError:
        return f"{package_name} not found"


version = get_package_version("damona")


# The logger mechanism is here:
handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter("%(log_color)s%(levelname)s: [%(name)s,l %(lineno)s]: %(message)s"))
logger = colorlog.getLogger("damona")
logger.addHandler(handler)

# Here we create a persistent config directory in the Home of the user.
# This is a small file.
from damona.config import Config

try:
    Config()
except Exception:  # pragma: no cover
    logger.warning("Could not create a persistent config file in your home. Unexpected error.")


# the following statement checks existence of environemental variables (DAMONA_PATH, DAMONA_EXE, etc)
from damona.common import DamonaInit

DamonaInit()


from damona.common import Damona
from damona.environ import Environ, Environment

# The user/developer API
from damona.registry import Registry


def check_for_updates(package_name, current_version, timeout=2):
    """Check PyPI for a newer version of *package_name* and warn the user.

    Performs a lightweight HTTP request to the PyPI JSON API.  If a newer
    version is found a warning is logged; if the versions are equal an info
    message is logged.  Network errors are caught and logged as warnings so
    that they never prevent Damona from starting.

    :param str package_name: The distribution name to look up (e.g.
        ``"damona"``).
    :param str current_version: The currently installed version string.
    :param int timeout: Maximum seconds to wait for the PyPI response before
        giving up (default ``2``).
    """
    import json

    import requests
    from packaging import version

    # Get the current version of the installed package
    # Fetch the latest version from PyPI
    url = f"https://pypi.org/pypi/{package_name}/json"

    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()  # Raise an error for bad status codes (e.g. 404)
        data = response.json()
        latest_version = data["info"]["version"]

        # Compare versions and notify the user
        if version.parse(latest_version) > version.parse(current_version):
            logger.warning(
                f"\u26a0\ufe0f A new version ({latest_version}) of {package_name} is available! You have {current_version}. Use 'pip install damona --upgrade'"
            )
        else:
            logger.info(f"\u2705 You are using the latest version of {package_name} ({current_version}).")
    except requests.ConnectionError:
        logger.warning("No internet connection. Unable to check for updates.")
    except requests.Timeout:
        logger.warning("The request to check for updates timed out.")
    except requests.RequestException as e:
        logger.error(f"An error occurred: {e} while checking for updates")


check_for_updates("damona", version)


from loguru import logger

# Remove default handler
logger.remove()

# Configure loguru with color output and file logging
logger.add(sys.stderr, level="INFO", format="<green>{time}</green> | <level>{level}</level> | <cyan>{message}</cyan>")
