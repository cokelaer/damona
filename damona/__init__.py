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
import importlib.metadata as metadata
import os

import colorlog


def get_package_version(package_name):
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
except:  # pragma: no cover
    logger.warning("Could not create a persistent config file in your home. Unexpected error.")


# the following statement checks existence of environemental variables (DAMONA_PATH, DAMONA_EXE, etc)
from damona.common import DamonaInit

DamonaInit()


from damona.common import Damona
from damona.environ import Environ, Environment

# The user/developer API
from damona.registry import Registry



def check_for_updates(package_name, current_version, timeout=2):
    # local import

    import requests
    import json
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
            logger.warning(f"\u26a0\ufe0f A new version ({latest_version}) of {package_name} is available! You have {current_version}. Use 'pip install damona --upgrade'")
        else:
            logger.info(f"\u2705 You are using the latest version of {package_name} ({current_version}).")
    except requests.ConnectionError:
        logger.warning("No internet connection. Unable to check for updates.")
    except requests.Timeout:
        logger.warning("The request to check for updates timed out.")
    except requests.RequestException as e:
        logger.error(f"An error occurred: {e} while checking for updates")



check_for_updates("damona", version)



