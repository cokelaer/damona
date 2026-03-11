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
"""The Damona configuration"""
import pathlib

import colorlog
from easydev import CustomConfig

import damona.shell

logger = colorlog.getLogger(__name__)


__all__ = ["Config", "get_damona_commands"]


class Config:
    """A place holder to store our configuration file and shell scripts


    This class is called each time damona is started. The config file, if not present
    is created, otherwise nothing happens. Same for the bash and fish shell configuration
    files

    The damona configuration file looks like::

        [general]
        quiet=False

        [zenodo]
        token=APmm6p....
        orcid=0000-0001
        name='Cokelaer, Thomas'
        affiliation='Institut Pasteur'

        [sandbox.zenodo]
        token=FFmbAEhQbb...
        orcid=0000-0001
        name='Cokelaer, Thomas'
        affiliation='Institut Pasteur'

    Where the urls section can be used to store aliases to external registry. When
    installing software using::

        damona install example --url damona

    if the alias damona is in the [urls] section, it is replaced by its real value (https://...)
    the URL must end with the expected registry name **registry.txt**

    The zenodo section is not save by default since it is for developpers only.


    """

    def __init__(self, name="damona", urls={"damona": "https://biomics.pasteur.fr/salsa/damona/registry.txt"}):
        configuration = CustomConfig(f"{name}", verbose=True)

        #  let us add a damona.cfg in it. This will store URLs to look for singularities
        # This is done only once to not overwrite user options
        self.user_config_dir = pathlib.Path(configuration.user_config_dir)

        self.config_file = self.user_config_dir / "damona.cfg"
        self.user_config_dir.mkdir(parents=True, exist_ok=True)
        if not self.config_file.exists():
            with open(self.config_file, "w") as fout:
                fout.write("[general]\n")
                fout.write("verbose=True\n\n")
                fout.write("[urls]\n")
                for k, v in urls.items():
                    fout.write("{}={}".format(k, v))
        else:
            logger.debug("damona.cfg file exists already. Reading it")

        # read the config
        self.read()

        # create the shell script once for all
        bash_created = self.add_bash()
        fish_created = self.add_fish()
        zsh_created = self.add_zsh()

        # Auto-configure shell RC files so users don't need to add source lines manually.
        # Only do this for the production config (not test configs).
        if name == "damona":
            self._init_bash_rc()
            self._init_fish_rc()
            self._init_zsh_rc()

        if bash_created or fish_created or zsh_created:  # pragma: no cover
            logger.critical(
                "Please start a new shell to benefit from " "the configuration file and activate/deactivate command"
            )
            # sys.exit(1)

    def read(self):
        """Reads the config file"""
        from configparser import ConfigParser

        config = ConfigParser()
        config.read(str(self.config_file))
        self.config = config

    def _copy_shell_file(self, source, dest):
        """Copy source shell file to dest, returning True if the file was created or updated."""
        shell_path = pathlib.Path(damona.shell.__path__[0])
        new_content = (shell_path / source).read_text()
        dest_path = self.user_config_dir / dest
        if dest_path.exists():
            existing_content = dest_path.read_text()
            if existing_content == new_content:
                return False
            logger.warning(f"Updating {dest} in {self.user_config_dir}.")
        else:
            logger.warning(f"Creating {dest} file in {self.user_config_dir}.")
        dest_path.write_text(new_content)
        return True

    def add_bash(self):  # pragma: no cover
        return self._copy_shell_file("bash/damona.sh", "damona.sh")

    def add_zsh(self):  # pragma: no cover
        return self._copy_shell_file("zsh/damona.zsh", "damona.zsh")

    def add_fish(self):
        return self._copy_shell_file("fish/damona.fish", "damona.fish")

    def _update_shell_rc(self, rc_file, source_line, init_block, shell_name):
        """Append init_block to rc_file if source_line is not already present.

        Returns True if the file was modified, False if already configured or
        if the operation failed.
        """
        rc_path = pathlib.Path(rc_file).expanduser()
        try:
            rc_path.parent.mkdir(parents=True, exist_ok=True)
            if rc_path.exists() and source_line in rc_path.read_text():
                return False
            with open(rc_path, "a") as fout:
                fout.write(init_block)
            logger.warning(
                f"Added damona {shell_name} initialization to {rc_file}. "
                "Please start a new terminal for the changes to take effect."
            )
            return True
        except Exception as e:
            logger.debug(f"Could not update {rc_file}: {e}")
            return False

    def _init_bash_rc(self):
        """Add damona bash initialization to ~/.bashrc if not already present."""
        block = (
            "\n# Added by Damona\n"
            "if [ -f ~/.config/damona/damona.sh ] ; then\n"
            "    source ~/.config/damona/damona.sh\n"
            "fi\n"
        )
        return self._update_shell_rc("~/.bashrc", "source ~/.config/damona/damona.sh", block, "bash")

    def _init_zsh_rc(self):
        """Add damona zsh initialization to ~/.zshrc if not already present."""
        block = (
            "\n# Added by Damona\n"
            "if [ -f ~/.config/damona/damona.zsh ] ; then\n"
            "    source ~/.config/damona/damona.zsh\n"
            "fi\n"
        )
        return self._update_shell_rc("~/.zshrc", "source ~/.config/damona/damona.zsh", block, "zsh")

    def _init_fish_rc(self):
        """Add damona fish initialization to ~/.config/fish/config.fish if not already present."""
        block = (
            "\n# Added by Damona\n"
            "if test -f ~/.config/damona/damona.fish\n"
            "    source ~/.config/damona/damona.fish\n"
            "end\n"
        )
        return self._update_shell_rc(
            "~/.config/fish/config.fish", "source ~/.config/damona/damona.fish", block, "fish"
        )


def get_damona_commands():
    """Print commands available in Damona if not hidden.

    This function is used for the fish completion"""
    from damona import script

    commands = [x for x in dir(script) if "allow_interspersed_args" in dir(getattr(script, x))]
    commands = [x for x in commands if not getattr(script, x).hidden]
    commands = [x for x in commands if x != "main"]
    print("\n".join(commands))
