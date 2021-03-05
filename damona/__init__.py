import pkg_resources
import os
import pathlib
import colorlog

try:
    version = pkg_resources.require("damona")[0].version
except Exception:   #pragma: no cover
    version = ">=0.8.3"


# The logger mechanism is here:
handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(
    '%(log_color)s%(levelname)s: [%(name)s,l %(lineno)s]: %(message)s'))
logger = colorlog.getLogger("damona")
logger.addHandler(handler)


# Here we create a persistent config directory in the Home of the user.
# This is a small file.
from damona.config import Config
Config()



 # Some information for the users
if "DAMONA_EXE" not in os.environ: #pragma: no cover
    #logger.critical("No DAMONA_EXE environment variable found")
    logger.critical("Damona binaries are installed in ~/.config/damona/bin by default")
    logger.critical("You may install them in specific environments and activate/deactivate"
        " the environments to you convenience.")
    logger.critical("You will need to set the PATH manually so that you may "
        "find binaries in ~/.config/damona/bin or one of the environment "
        "in ~/.config/damona/envs")
    logger.critical("To remove this message, and benefit from the "
        "activate/deactivate command, add this line in your .bashrc\n"
        "source ~/.config/damona/damona.sh\n")


# Based on the previous config path, we may add images, environments and
# binaries if  DAMONA_PATH is not defined. If DAMONA_PATH is redefined,
# the following call creates the images/ envs/ bin/ directories
from damona.common import DamonaInit
DamonaInit()


# The user/developer API
from damona.registry import Registry
from damona.environ import Environ, Environment
from damona.common import Damona
