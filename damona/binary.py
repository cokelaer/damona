# -*- coding: utf-8 -*-
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
#  website: https://github.com/damona/damona
#  documentation: http://damona.readthedocs.io
#
##############################################################################

import pathlib
import os

from damona import logger
from damona import Environ


class Binary():
    """Install a binary the bin/ directory of current environment

    If the singularity image is EXE, then just create a single
    alias to the singularity based on the registry name. If not,
    a list of binaries is required

        from damona import Binary
        b = Binary("images/bowtie2_2.1.0.img")
        # install in current environment
        b.install_executable_image("bowtie2")

    """
    def __init__(self, image_path, dryrun=False):
        self.image_path = image_path
        self.dryrun = dryrun

    def install_executable_image(self, registry_name, force=False):
        """Install an image and its binary 

        TODO: this should not install the image itself, only the binary"""
        env = Environ()
        bin_directory = env.get_current_env() + "/bin"

        bin_path = pathlib.Path(bin_directory) / registry_name.split("_")[0]

        from damona.install import LocalImageInstaller
        ii = LocalImageInstaller(self.image_path)

        cmd = """singularity -s run {} ${{1+"$@"}}"""

        cmd = cmd.format(ii.target)

        if self.dryrun: #pragma: no cover
            logger.warning("Binary {} not created (--dryrun used)".format(bin_path))
        else: #pragma: no cover
            if bin_path.exists() and force is False:
                logger.warning("Binary exists already. Use --force to overwrite")
            else:
                # create binary and set correct permission
                with open(bin_path, "w") as fout:
                    fout.write(cmd)
                os.chmod(bin_path, 0o755)

                # aliases to print message
                name = pathlib.Path(bin_path).name
                path = str(bin_path).rstrip(bin_path.name)
                logger.info(f"Created binary {name} in {path}")


class SET():
    """Install aliases to be found in a container

    If the singularity image is SET, we can create several binary from the
    container

    """
    def __init__(self, image_path, dryrun=False):
        self.image_path = image_path
        self.dryrun = dryrun

    def install_executable_image(self, binaries):
        env = Environ()
        bin_directory = env.get_current_env() + "/bin"


        cmd = """singularity -s run {} {} ${{1+"$@"}}"""

        if self.dryrun: #pragma: no cover
            logger.warning("Binary {} not created (--dryrun used)".format(bin_directory))
        else: #pragma: no cover
            for binary in binaries:
                bin_path = pathlib.Path(bin_directory) / binary
                with open(bin_path, "w") as fout:
                    fout.write(cmd.format(self.image_path, binary))
                os.chmod(bin_path, 0o755)

                # aliases to print message
                print(bin_path)

                name = pathlib.Path(bin_path).name
                path = str(bin_path).rstrip(bin_path.name)
                logger.info(f"Created binary {bin_path} in {path}")



