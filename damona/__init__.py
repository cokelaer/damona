import pkg_resources
import os
import pathlib

try:
    version = pkg_resources.require("damona")[0].version
except:   #pragma: no cover
    version = ">=0.8.3"


import colorlog

handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(
	'%(log_color)s%(levelname)s:%(name)s: %(message)s'))
logger = colorlog.getLogger("damona")
logger.addHandler(handler)

# This code will create the config directory if it does not exists
from easydev import CustomConfig
configuration = CustomConfig("damona", verbose=True)
damona_config_path = configuration.user_config_dir


# let us add a damona.cfg in it. This will store URLs to look for singularities
# This is done only once to not overwrite user options
from damona.config import Config
Config()

# We should not write the file each time we start damona but only if it does not
# exists; New version will be install only when calling python setup.py in dev
# or install modes.

if os.path.exists(damona_config_path + os.sep + "damona.sh") is False:
    import damona.shell
    shell_path = damona.shell.__path__._path[0]
    with open(shell_path + os.sep + "damona.sh", "r") as fin:
        with open(damona_config_path + os.sep + "damona.sh", "w") as fout:
            fout.write(fin.read())
 
if "DAMONA_EXE" not in os.environ: #pragma: no cover
    #logger.critical("No DAMONA_EXE environment variable found")
    logger.critical("Damona binaries are installed in .config/damona/bin by default")
    logger.critical("You may install them in specific environments and activate/deactivate"
        " the environments to you convenience.")
    logger.critical("You will need to set the PATH manually so that you may "
        "find binaries in ~/.config/damona/bin or one of the environment "
        "in ~/.config/damona/envs")
    logger.critical("To remove this message, and benefit from the "
        "activate/deactivate command, add this line in your .bashrc\n"
        ". ~/.config/damona/damona.sh\n")




# Let us create some extra directories
_damona_path = pathlib.Path(damona_config_path)
# First the env directory then, the sub-directories. 
try:
    env_directory = _damona_path / 'envs'
    env_directory.mkdir()
except: # pragma: no cover
    pass # exists already

try:
    _bin_directory = _damona_path / 'bin'
    _bin_directory.mkdir()
except: # pragma: no cover
    pass # exists already

try:
    images_directory = _damona_path / 'images'
    images_directory.mkdir()
except: #pragma: no cover
    pass # exists already

from damona.registry import Registry
from damona.environ import Environ
