#  This file is part of Damona software
#
#  Copyright (c) 2020-2021 - Damona Development Team
#
#  File author(s):
#      Thomas Cokelaer <thomas.cokelaer@pasteur.fr>
#          <d.desvillechabrol@gmail.com>
#
#  Distributed under the terms of the 3-clause BSD license.
#  The full license is in the LICENSE file, distributed with this software.
#
#  website: https://github.com/cokelaer/damona
#  documentation: http://damona.readthedocs.io
#
##############################################################################
"""The Damona configuration"""
import os
import pathlib

from easydev import CustomConfig

import colorlog
            
import damona.shell

logger = colorlog.getLogger(__name__)


# list of URLs where to find registry and their aliases
urls = {"damona": "https://biomics.pasteur.fr/salsa/damona/registry.txt"}


__all__ = ["Config"]


class Config:
    """A place holder to store our configuration file and shell scripts

    ::

        [urls]
        damona=https://....
        url1=https://....

    """

    def __init__(self, name="damona"):
        configuration = CustomConfig(f"{name}", verbose=True)

        #  let us add a damona.cfg in it. This will store URLs to look for singularities
        # This is done only once to not overwrite user options
        self.user_config_dir = pathlib.Path(configuration.user_config_dir)

        self.config_file = self.user_config_dir / "damona.cfg"
        if self.config_file.exists() is False:  # pragma: no cover
            with open(self.config_file, "w") as fout:
                fout.write("[general]\n")
                fout.write("quiet=False\n\n")
                fout.write("[urls]\n")
                for k, v in urls.items():
                    fout.write("{}={}".format(k, v))
        else:
            logger.debug("damona.cfg file exists already. Reading it")

        # read the config
        self.read()

        # create the shell script once for all
        created = self.add_shell()
        created = self.add_fish()
        if created:  # pragma: no cover
            logger.critical(
                "Please start a new shell to benefit from " "the configuration file and activate/deactivate command"
            )
            # sys.exit(1)

    def read(self):
        from configparser import ConfigParser

        config = ConfigParser()
        config.read_file(open(self.config_file))
        self.config = config

    def add_shell(self):  # pragma: no cover  ; this is executed only if config does not exists
        #  let us add a damona.cfg in it. This will store URLs to look for singularities
        # This is done only once to not overwrite user options
        if os.path.exists(self.user_config_dir / "damona.sh") is False:
            logger.info("adding a damona.sh in your DAMONA_PATH")
            _damona_config_path = self.user_config_dir
            logger.warning(f"Creating damona.sh file in {_damona_config_path}. ")

            shell_path = pathlib.Path(damona.shell.__path__[0])
            with open(shell_path / "bash" /  "damona.sh", "r") as fin:
                with open(_damona_config_path / "damona.sh", "w") as fout:
                    fout.write(fin.read())
            return True
        else:
            return False

    def add_fish(self):
        if os.path.exists(self.user_config_dir/ "damona.fish") is False:
            logger.info("adding a damona.fish in your DAMONA_PATH")
            _damona_config_path = self.user_config_dir
            logger.warning(f"Creating damona.fish file in {_damona_config_path}. ")

            shell_path = pathlib.Path(damona.shell.__path__[0])
            with open(shell_path / "fish" /  "damona.fish", "r") as fin:
                with open(_damona_config_path / "damona.fish", "w") as fout:
                    fout.write(fin.read())
            return True
        else:
            return False


def get_damona_commands():
    """Print commands. This is for the fish completion"""
    from damona import script 
    commands = [x for x in dir(script) if "allow_interspersed_args" in dir(getattr(script, x))]
    commands = [x for x in commands if not getattr(script, x).hidden]
    commands = [x for x in commands if x != "main"]
    print("\n".join(commands))


