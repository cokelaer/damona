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
