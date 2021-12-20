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
"""Image and Binary handlers. Provide also a Damona manager"""
import os
import sys
import pathlib
import re
import subprocess

from easydev import md5


import colorlog

logger = colorlog.getLogger(__name__)


__all__ = ["Damona", "ImageReader", "BinaryReader", "DamonaInit"]


class DamonaInit:
    """Class to create images/bin directory for DAMONA


    This is called each time damona is started to make sure
    required config file are present.
    """

    def __init__(self):
        if "DAMONA_PATH" not in os.environ:
            try:
                HOME = os.path.expanduser("~")
            except Exception:  # pragma: no cover
                HOME = "/home/user/"
            logger.error(
                """DAMONA_PATH was not found in your environment.

Before using Damona, you have to copy/paste the following code in
your ~/.bashrc file once for all (start a new shell afterwards):

    if [ ! -f  "~/.config/damona/damona.sh" ] ; then
        source ~/.config/damona/damona.sh
    fi

This will create DAMONA_PATH variable that points to your home/.config/damona/ directory.
You can redefine the DAMONA_PATH later to point towards another path if needed."""
            )
            sys.exit(1)

        if "DAMONA_SINGULARITY_OPTIONS" not in os.environ:
            logger.warning(
                """No DAMONA_SINGULARITY_OPTIONS variable found in your environment.
To remove this message, set a DAMONA_SINGULARITY_OPTIONS variable in your shell. For explanation about
this variable, please see https://damona.readthedocs.io/en/latest/userguide.html#DAMONA_SINGULARITY_OPTIONS """
            )

        self.damona_path = pathlib.Path(os.environ["DAMONA_PATH"])
        os.makedirs(self.damona_path, exist_ok=True)
        os.makedirs(self.damona_path / "envs" / "base" / "bin", exist_ok=True)
        os.makedirs(self.damona_path / "images" / "damona_buffer", exist_ok=True)


class Damona:
    """Global manager to handle environments, registy, perform general
    task such as cleaning.

    """

    def __init__(self):

        if "DAMONA_PATH" not in os.environ:
            logger.error(
                "DAMONA_PATH not found in your environment. You must define "
                "it. In this shell, type 'export DAMONA_PATH=PATH_WHERE_TO_PLACE_DAMONA'"
            )
            sys.exit(1)
        self.damona_path = pathlib.Path(os.environ["DAMONA_PATH"])

    def _get_config_path(self):
        return self.damona_path / "damona.cfg"

    config_path = property(_get_config_path)

    def _get_image_directory(self):
        return self.damona_path / "images"

    images_directory = property(_get_image_directory)

    def _get_environments_path(self):
        return self.damona_path / "envs"

    environments_path = property(_get_environments_path)

    def find_orphan_binaries(self):
        """Find binaries in all environments that are orphans

        By orphans, we mean that their image is not present anymore so some
        reasons.
        """
        binaries = self.get_all_binaries()
        orphans = []
        for x in binaries:
            br = BinaryReader(x)
            if br.is_image_available() is False:  # pragma: no cover
                logger.warning(f"{x} image is not available. This binary is an orphan")
                orphans.append(x)
        return orphans

    def get_environments(self):
        from damona.environ import Environ

        env = Environ()
        return env.environment_names

    def get_all_binaries(self):
        """Return list of all binaries in all environments"""
        from damona.environ import Environ

        env = Environ()
        binaries = [e.get_installed_binaries() for e in env.environments]
        binaries = set([x for y in binaries for x in y])
        return binaries

    def find_orphan_images(self):
        """Get images that have no binaries in any environments"""
        binaries = self.get_all_binaries()
        images = self.get_all_images()
        Nb = len(binaries)
        Ni = len(images)

        print(f"Found {Ni} images and {Nb} binaries. Checking consistencies")
        used_images = []
        for binary in binaries:
            br = BinaryReader(binary)
            used_images.append(pathlib.Path(br.image))

        used_images = set(used_images)
        Nu = len(used_images)
        No = Ni - Nu
        print(f"{Nu} images is/are used. Meaning {No} are orphans and could be removed")
        orphans = []

        for image in images:
            if image not in used_images:
                logger.info(f"{image} image not used in any environments")
                orphans.append(image)
        return orphans

    def get_all_images(self):
        """Return list of all images"""
        from damona.environ import Images

        images = Images()
        return list(images.files)


class ImageReader:
    """Manage a single image"""

    def __init__(self, name):
        """

        :param name: the input name of the image (fullpath)

        ::

            ir = ImageReader("fastqc.img")
            ir.md5
            ir.is_orphan()
            ir.name
            ir.shortname

        """
        self.filename = pathlib.Path(name)

        if self.is_valid_name() is False:
            logger.error("Invalid image name. Your input image must end in .img or .sif")
            sys.exit(1)

    def _get_short_name(self):
        return self.filename.name

    shortname = property(_get_short_name)

    def is_valid_name(self):
        pattern = r".+_(v|)\d+\.\d+\.\d+(.+|)\.(img|sif)"
        p = re.compile(pattern)
        if p.match(self.shortname):
            return True
        else:
            return False

    def _get_executable_name(self):
        pattern = r"_(v|)\d+\.\d+\.\d+(.+|)\.(img|sif)"
        p = re.compile(pattern)
        ss = p.search(self.shortname)
        guess = self.shortname[0 : ss.span()[0]]
        return guess

    guessed_executable = property(_get_executable_name)

    def _get_version(self):
        pattern = r"_(v|)\d+\.\d+\.\d+(.+|)\.(img|sif)"
        p = re.compile(pattern)
        ss = p.search(self.shortname)
        version = ss.group().replace(".sif", "").replace(".img", "")
        if version[0] == "_":
            version = version[1:]
        if version[0] == "v":
            version = version[1:]
        return version

    version = property(_get_version)

    def _get_md5sum(self):
        md5sum = md5(self.filename)
        return md5sum

    md5 = property(_get_md5sum)

    def is_orphan(self):
        binaries = Damona().get_all_binaries()
        linked_binaries = []
        for binary in binaries:
            if self.filename == BinaryReader(binary).image:
                linked_binaries.append(binary)
        if len(binaries) == 0:
            return True
        else:
            return False

    def is_installed(self):
        damona_path = pathlib.Path(os.environ["DAMONA_PATH"])
        if (damona_path / "images" / self.filename.name).exists():
            return True
        else:
            return False

    def __repr__(self):
        txt = f"name: {self.filename.absolute()}\n"
        txt += f"shortname: {self.shortname}\n"
        txt += f"md5: {self.md5}\n"
        txt += f"version: {self.version}\n"
        txt += f"guessed executable: {self.guessed_executable}"
        return txt


class BinaryReader:
    """Manage a single binary"""

    def __init__(self, filename):
        """

        :param name: the input name of the binary file

        Can be use to check whether the binary is not orphan and its image is
        still available.

        """
        logger.debug(f"{filename}")
        if isinstance(filename, str):
            filename = pathlib.Path(filename)
        self.filename = filename

        with self.filename.open("r") as fin:

            data = [x for x in fin.readlines() if x.strip().startswith("singularity")]
            data = data[0]

            data = data.replace("${DAMONA_SINGULARITY_OPTIONS}", "")
            try:
                image_path = data.split("exec")[1].split()[0]
            except:  # pragma: no cover
                image_path = data.split("run")[1].split()[0]
                logger.warning(f"command line in {self.filename} uses 'run'; should be reinstalled ")

            if "DAMONA_PATH" in os.environ:
                DAMONA_PATH = os.environ["DAMONA_PATH"]
                self.image = image_path.replace("${DAMONA_PATH}", DAMONA_PATH)
            else:
                self.image = image_path

    def is_image_available(self):
        if "DAMONA_PATH" not in os.environ:
            logger.error("You must define DAMONA_PATH")
            sys.exit(1)

        damona_path = os.environ["DAMONA_PATH"]
        if os.path.exists(self.image.replace("${DAMONA_PATH}", damona_path)):
            return True
        else:
            return False

    def get_image(self):
        # we assume the user did not edit the binary file
        # so we expect one uncommented line
        with self.filename.open("r") as fin:
            command = [line for line in fin.readlines() if line.strip() and line.strip()[0] != "#"]
        # where /images is to be followed by the container
        image = [x for x in command[0].split() if "/images/" in x]
        image = image[0].split()
        container = image[0].split("/")[-1]
        container = container.replace(".img", "")
        container = ":".join(container.rsplit("_", 1))
        return container
