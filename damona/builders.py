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
import pathlib
import re
import subprocess
import sys
import tempfile

from damona.common import Damona, get_container_cmd, requires_singularity

manager = Damona()


import colorlog

logger = colorlog.getLogger(__name__)

__all__ = ["Builder", "BuilderFromSingularityRecipe", "BuilderFromDocker", "get_bootstrap_info", "fetch_base_image"]


def get_bootstrap_info(recipe):
    """Return the (bootstrap, from) header fields of a Singularity recipe.

    Both values are lower-cased for the key lookup but the ``From`` value is
    returned unchanged. Missing fields are returned as ``None``.

    :param recipe: path to a Singularity recipe.
    :rtype: tuple
    """
    bootstrap, source = None, None
    with open(recipe, "r") as fh:
        for line in fh:
            match = re.match(r"^\s*(bootstrap|from)\s*:\s*(\S+)", line, flags=re.IGNORECASE)
            if match:
                key = match.group(1).lower()
                if key == "bootstrap":
                    bootstrap = match.group(2).lower()
                else:
                    source = match.group(2)
            # header fields are always before the first section
            if line.startswith("%"):
                break
    return bootstrap, source


def fetch_base_image(recipe):
    """Download the local base image required by a recipe if it is missing.

    Recipes based on ``Bootstrap: localimage`` refer to an image stored inside
    the Damona repository (e.g. ``../../library/micromamba/micromamba_2.5.0.img``).
    Those images are not tracked by git, so they are missing from a fresh clone
    or after a cleanup. Here we resolve the image path relatively to the recipe,
    and if the image is not found, we download it from the registry of the
    corresponding software (in *library* or *software* directory).

    :param recipe: path to a Singularity recipe.
    :return: the resolved path of the base image, or None if the recipe does not
        rely on a local image.
    """
    bootstrap, source = get_bootstrap_info(recipe)

    if bootstrap != "localimage" or source is None:
        return None

    # apptainer resolves the From path from the current directory, but recipes are
    # written relatively to their own location (usually the same thing since one
    # builds from the recipe directory). We accept both, and download in the latter.
    image = (pathlib.Path(recipe).resolve().parent / source).resolve()
    for candidate in (image, pathlib.Path(source).resolve()):
        if candidate.exists():
            logger.debug(f"Base image {candidate} found locally.")
            return candidate

    logger.info(f"Base image {image} not found. Trying to download it from the Damona registry.")

    # images are named NAME_x.y.z.img by convention
    try:
        name, version = image.name[: -len(image.suffix)].rsplit("_", 1)
    except ValueError:  # pragma: no cover
        logger.error(f"Cannot guess the software name/version from {image.name} (expected NAME_x.y.z{image.suffix}).")
        sys.exit(1)

    from damona.registry import Software

    software = Software(name)
    if version not in software.releases:
        logger.error(
            f"No release {version} found in the registry of {name} ({software.registry_name}). "
            f"Available: {software.versions}"
        )
        sys.exit(1)

    release = software.releases[version]

    from damona.utils import download_with_progress

    download_with_progress(release.download, filename=str(image))

    if release.md5sum:
        from easydev import md5

        if md5(image) != release.md5sum:  # pragma: no cover
            logger.error(
                f"MD5 of the downloaded base image {image} does not match the registry "
                f"({software.registry_name}). Download may have been interrupted."
            )
            sys.exit(1)

    logger.info(f"Base image downloaded in {image}")
    return image


class Builder:
    """Build a container using different framework

    Input can be a singularity or docker container/recipes.

    """

    def __init__(self):
        """.. rubric:: **Constructor**"""
        pass

    def get_temp_file(self):
        """Return a named temporary file in the Damona config directory.

        :returns: A :class:`tempfile.NamedTemporaryFile` with a ``.img`` suffix.
        """
        # note: manager.config_path is the damona.cfg *file*, not a directory,
        # so the temporary file must be created in manager.damona_path instead
        filename = tempfile.NamedTemporaryFile(dir=manager.damona_path, suffix=".img")
        return filename

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
        """.. rubric:: **Constructor**"""
        super(BuilderFromDocker, self).__init__()
        logger.info("Building a singularity image from docker")

    @requires_singularity
    def build(self, dockerhub_name, destination=None, force=False):
        """Build the singularity image from docker image"""

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
                    "The container has no version using the v: separator (e.g., bowtie2:v1.0.0). No destination was provided either; please use e.g. --destination NAME_X.Y.Z.img where X.Y.Z is te version"
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
        cmd = f"{get_container_cmd()} pull --force {destination} docker://{dockerhub_name} "
        logger.info(f"Running : {cmd}")
        subprocess.call(cmd.split())

        self.teardown(destination)


class BuilderFromSingularityRecipe(Builder):
    """Build a container from its singularity recipe

    This command creates the destination file bowtie2_2.4.1.img::

        damona build Singularity.bowtie2_2.4.1

    """

    def __init__(self):
        """.. rubric:: **Constructor**"""
        super(BuilderFromSingularityRecipe, self).__init__()
        logger.info("Building a Singularity image from a Singularity recipe")

    @requires_singularity
    def build(self, recipe, destination=None, force=False):
        """Build a Singularity image from a local recipe file.

        :param str recipe: Path to the Singularity recipe.  The basename must
            start with ``Singularity.``.
        :param str destination: Output ``.img`` filename.  If ``None``, derived
            from the recipe name by removing the ``Singularity.`` prefix.
        :param bool force: Overwrite an existing destination file without
            prompting (default ``False``).
        :raises SystemExit: When the recipe name is invalid, the build fails,
            or the user declines to overwrite an existing file.
        """
        if os.path.basename(recipe).startswith("Singularity.") is False:
            logger.error("Recipe must start with Singularity.")
            sys.exit(1)

        # recipes based on a local image (e.g. micromamba) require that image to be
        # present; it is not tracked by git so we may have to download it first.
        fetch_base_image(recipe)

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
        cmd = f"{get_container_cmd()} build --force {destination} {recipe} "
        logger.info(f"Running : {cmd}")
        status = subprocess.call(cmd.split())
        if status != 0:  # pragma: no cover
            logger.error("An error occurred")
            sys.exit(1)

        self.teardown(destination)
