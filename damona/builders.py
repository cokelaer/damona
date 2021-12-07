#
#  This file is part of Damona software
#
#  Copyright (c) 2016 - Damona Development Team
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
"""Builder for containers from docker or singularity images"""
import os
import subprocess
import sys
import tempfile
import getpass

from damona.common import Damona

manager = Damona()


import colorlog

logger = colorlog.getLogger(__name__)

__all__ = ["Builder", "BuilderFromSingularityRecipe", "BuilderFromDocker"]


class Builder:
    """Build a container using different framework

    Input can be a singularity or docker container.

    """

    def __init__(self):
        # just to check that a username is defined before building the image
        self.username

    def get_temp_file(self):
        filename = tempfile.NamedTemporaryFile(dir=manager.config_path, suffix=".img")
        return filename

    def _get_username(self):
        username = getpass.getuser()
        # if 'USERNAME' not in os.environ:
        #    logger.critical('USERNAME was not found in your environment. Must be'
        #        ' defined in your environement to change permission of the built'
        #        ' image. Keep going but your image will have ownership of root'
        #        ' user only')
        return username

    username = property(_get_username, doc="return the username (unix)")

    def teardown(self, dest):
        """finalise the build

        Currently, just print information
        """
        # once built and install, we can stop and save information in
        #  the history if it was susccessul
        logger.info(f"Image built in {dest}")


class BuilderFromDocker(Builder):
    """Install a singularity container image and executable from a docker hub container.

    This command creates automatically the destination bowtie2_2.4.1.img because the version
    follows Damona convention::

        damona build docker://biocontainers/bowtie2:v2.4.1_cv1

    This command will fail::

        damona build docker://alpine

    but this one will tell the version::

        damona build docker://alpine --destination alpine_1.0.0.img

    We assume that the name of the executable is the name of the container.
    User may provide a binary or list of binaries to install from the container if it is known.
    """

    def __init__(self):
        super(BuilderFromDocker, self).__init__()
        logger.info("Building a singularity image from docker")

    def build(self, dockerhub_name, destination=None, force=False):

        # if the build is successful, we will copy the image
        # into the current environment.
        # Let us check now the present of the image and its executable
        if destination is None:  # pragma: no cover
            if ":v" in dockerhub_name:
                name, version = dockerhub_name.split(":v")
                name = name.split("/")[-1]
                destination = name + "_" + version + ".img"
            else:
                logger.error(
                    "The container has no version using the v: separator (e.g., bowtie2:v1.0.0). No destination was provided either."
                )
                sys.exit(1)
        else:
            if destination.endswith(".sif") is False and destination.endswith(".img") is False:
                logger.error("destination name must end in .sif or .img")
                sys.exit(1)

        if os.path.exists(destination):
            answer = None
            if force is True:
                answer = "yes"
            while answer not in ["yes", "no"]:
                answer = input(f"Image ({destination}) exists already in Damona, do you want to overwrite it ?")
                if answer == "no":
                    return
                elif answer == "yes":
                    pass
                else:
                    logger.error("please answer yes or no")
                    sys.exit(1)

        # build the image
        cmd = f"sudo singularity pull --force {destination} docker://{dockerhub_name} "
        logger.info(f"Running : {cmd}")
        subprocess.call(cmd.split())

        cmd = f"sudo chown {self.username}:{self.username} {destination}"
        subprocess.call(cmd.split())

        self.teardown(destination)


class BuilderFromSingularityRecipe(Builder):
    """Build a container from its singularity recipe"""

    def __init__(self):
        super(BuilderFromSingularityRecipe, self).__init__()
        logger.info("Building a Singularity image from a Singularity recipe")

    def build(self, recipe, destination=None, force=False):

        if os.path.basename(recipe).startswith("Singularity.") is False:
            logger.error("Recipe must start with Singularity.")
            sys.exit(1)

        if destination is None:  # FIXME: do the same as for docker files ?
            destination = os.path.basename(recipe).replace("Singularity.", "") + ".img"

        if os.path.exists(destination):
            answer = None
            if force is True:
                answer = "yes"
            while answer not in ["yes", "no"]:
                answer = input(f"Image ({destination}) exists already, do you want to overwrite it ?")
                if answer == "no":
                    return
                elif answer == "yes":
                    pass
                else:
                    logger.error("please answer yes or no")
                    sys.exit(1)

        # build the image
        cmd = f"sudo singularity build --force {destination} {recipe} "
        logger.info(f"Running : {cmd}")
        status = subprocess.call(cmd.split())
        if status != 0:  # pragma: no cover
            logger.error("An error occured")
            sys.exit(1)

        cmd = f"sudo chown {self.username}:{self.username} {destination}"
        subprocess.call(cmd.split())

        self.teardown(destination)
