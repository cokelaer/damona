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


# let us add a damona.cfg in it
from damona.config import Config
Config()



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
