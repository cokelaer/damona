#
#  This file is part of Damona software
#
#  Copyright (c) 2020 - Damona Development Team
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
"""Tools to install images/binaries"""
import os
import sys
import pathlib

import shutil
import time
import subprocess

from urllib.request import urlretrieve

from easydev import md5


from spython.main import Client
from damona import Registry
from damona import Environ
from damona.common import ImageReader, requires_singularity
from damona.registry import Software
from damona import version as damona_version


DAMONA_PATH = os.environ["DAMONA_PATH"]


import colorlog

logger = colorlog.getLogger(__name__)


__all__ = ["LocalImageInstaller", "RemoteImageInstaller", "BinaryInstaller"]


class CMD:
    def __init__(self, cmd):
        self.cmd = cmd
        self.version = damona_version

    def __repr__(self):
        if self.cmd[0].endswith("damona"):
            cmd = "damona " + " ".join(self.cmd[1:])
            return cmd
        else:  # not a correct damona command (maybe from pytest)
            return "#test"


class ImageInstaller:
    @requires_singularity
    def _are_binaries_findable(self):
        # TODO add sanity check that stops the installation if a failure occurs
        for binary in self.binaries:
            # is it found in the image ? without -v may return error code
            # so we first test with --version option but some tools will use -v
            # so we test --version and -v cases. Finally, if there is no
            # version, let us just try without arguments. Most probably an error
            # code is returned. ut if not found at all, a 'executable file not
            # found' message should be returned by bash. Not ideal but will do
            # for now.
            cmd1 = f"singularity exec {self.input_image.filename} {binary}"
            cmd2 = f"singularity exec {self.input_image.filename} {binary} -v"
            cmd3 = f"singularity exec {self.input_image.filename} {binary} --version"
            # ideally we should use commad but not present on all systems....
            # cmd = f"singularity exec {self.input_image.filename} command -v {binary}"

            status = subprocess.Popen(cmd3, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            status.wait()
            if status.returncode == 0:
                logger.info(f"'{binary}' binary found in the container. Planned to be installed")
                continue

            status = subprocess.Popen(cmd2, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            status.wait()
            if status.returncode == 0:  # pragma: no cover
                logger.info(f"'{binary}' binary found in the container. Planned to be installed")
                continue

            status = subprocess.Popen(cmd1, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            status.wait()
            if status.returncode == 0:  # pragma: no cover
                logger.info(f"'{binary}' binary found in the container. Planned to be installed")
                continue
            else:
                if status.stderr is None:
                    logger.critical("Unknown error due to errocode != 0 but not error message reported")
                    # FIXME. not sure this ever happens
                    return False

                error = status.stderr.read()
                if "executable file not found" in error.decode():
                    logger.critical(f"{binary} executable not available in the image {self.input_image.filename}")
                    return False
                else:
                    # Other type of error could simply be help printed to stderr...
                    # let us assume this is the case but let us print a warning
                    # for future debugging
                    logger.warning(
                        f"Error while testing presence of {binary}. Most probably related to missing arguments. Here is the error code returned: \n\n{error}\n\n Proceed"
                    )
        return True

    def install_binaries(self, force=False):
        if self.image_installed:
            bininst = BinaryInstaller(self.binaries, self.input_image.filename)
            bininst.install_binaries(force=force)
        else:
            logger.critical("The container image has not been installed. So, binaries cannot be installed either")


class LocalImageInstaller(ImageInstaller):
    """Install a local singularity image.


    When using the standalone, you can install a local singularity even though it is not registered.
    This is not recommended but very useful for developers::

        damona install fastqc_0.11.9.img --binaries fastqc

    Since there is no registry, you can set the list of binaries.

    """
    def __init__(self, image_name, cmd=None, binaries=None):
        """.. rubric:: **Constructor**

        :param str image_name: The location of the singularity image to be installed.
        :param cmd: internal place holder to fill the history log with the calling command.
        :param list binaries: The list of binaries to be installed and expected to be
            found in the :attr:`image_name`

        """
        # must be a valid name with version, name, etc so that executable name
        # can be guessed
        super(LocalImageInstaller, self).__init__()

        if os.path.exists(image_name) and pathlib.Path(image_name).is_dir():
            logger.error(f"image name must be a singulatity file, not a directory")
            sys.exit(1)

        self.input_image = ImageReader(image_name)
        self.target = pathlib.Path(DAMONA_PATH) / "images" / self.input_image.shortname
        self.images_directory = pathlib.Path(DAMONA_PATH) / "images"
        self.cmd = cmd

        # If no binaries are provided, we will guess from the name of the image
        # the unique possible binary to be found in the image.
        if binaries is None:
            self.binaries = [self.input_image.guessed_executable]
        else:
            self.binaries = binaries

        self.image_installed = False

    def is_valid(self):
        """Check whether binaries are findable in the image"""

        # let us check the  presence of the binaries in the image
        status = self._are_binaries_findable()
        return status

    def install_image(self, force=False):
        """Install the singularity image in the environment

        If an image exists with the same name, we check the md5sum of the destination and target.
        If they are identical, no need to overwrite the destination.
        """
        if (self.images_directory / self.input_image.shortname).exists():

            md5_target = md5(self.images_directory / self.input_image.shortname)
            if md5_target == self.input_image.md5:
                logger.info("Image with same md5 exists already. No need to copy")
                # image is not copied since it is already installed
                self.image_installed = True
            else:  # pragma: no cover
                if force:
                    self.copy()
                else:
                    logger.warning(
                        f"{self.input_image.filename} exists with different md5sum. Please use --force to overwrite"
                    )
        else:
            self.copy()

    def copy(self):  # pragma: no cover

        logger.info(f"Copying {self.input_image.filename} into {self.images_directory}")
        shutil.copy(self.input_image.filename, self.images_directory)
        with open(self.images_directory / "history.log", "a+") as fout:
            cmd = CMD(self.cmd).__repr__()
            fout.write(f"{time.asctime()}: {cmd}\n")
        # if the image has been copied properly, we set this flag to True so
        # that binaries can be installed
        self.image_installed = True


class RemoteImageInstaller(ImageInstaller):
    """Install a singulariy image and binaries from a damona registered image.

    The following command will download the fastqc singularity version 0.11.9
    from the damona website.::

        damona install fastqc:0.11.9

    It introspects all registry files to be found in damona package.

    However, if you have a damona registry on your website called registry.txt, you can download
    third-party images/software from any URL as follows::

        damona install fastqc:0.11.9 --url https://yourwebsite/.../registry.txt

    If you use this command often, you may want to add this line in your damona.cfg file. By
    default you should have this section in your config file::

        [urls]
        damona=https://biomics.pasteur.fr/salsa/damona/registry.txt

    so that you can simply type::

        damona install fastqc:0.11.9 --url damona

    """

    def __init__(self, image_name, binaries=None, from_url=None, cmd=None):
        """.. rubric:: **Constructor**

        :param str image_name: The location of the singularity image to be installed.
        :param list binaries: The list of binaries to be installed and expected to be
            found in the :attr:`image_name`
        :param cmd: internal place holder to fill the history log with the calling command.
        :param from_url: provide a URL if you want to use a third-party online registry

        """
        super(RemoteImageInstaller, self).__init__()

        self.image_name = image_name
        self.registry = Registry(from_url=from_url)
        self.images_directory = pathlib.Path(DAMONA_PATH) / "images"

        # if alias is given, this attribute contains the augmented (real) URL
        # but it contains registry.txt so we need to get rid of the registry filename
        try:
            self.from_url = self.registry.from_url.replace("registry.txt", "")
        except AttributeError:  # the url may not be set
            self.from_url = from_url
        self.cmd = cmd
        self.binaries = binaries
        self.image_installed = False

    def is_valid(self):

        return True

    @requires_singularity
    def pull_image(self, output_name=None, force=False):
        """Pull and Install a singularity image from the web.

        """

        self.image_installed = False

        # the name must be valid. we use _ to separate name and version for the
        # singularity filemane but the image have a tag (version) and name
        # separated by a :

        # Our registry uses underscore. The output filename should use _ as well
        # However, for users and image stored on sylabs or singularity hub, we
        # use the character :

        # let us first retrieve the image and save it in a temporary file.
        # we keep the original name by only replacing the : with underscore so
        # that we can use ImageReader class to help us later on.
        if ":" in self.image_name:
            logger.info(f"Looking for {self.image_name}...")
            # e.g. fastqc:0.11.9
            registry_name = self.image_name  # .replace(":", "_")

            if self.image_name not in self.registry.registry.keys():
                logger.critical("invalid image name provided: {}. type 'damona list'".format(self.image_name))
                guess = self.image_name.split(":")[0][0:4]
                # here we reverse x to start from the end and replace the last _
                # by :
                guesses = [
                    x[::-1].replace("_", ":", 1)[::-1] for x in self.registry.registry.keys() if x.startswith(guess)
                ]
                logger.critical("Maybe you meant one of: {}".format(guesses))
                sys.exit(1)
        else:

            soft = Software(self.image_name)

            try:
                r = soft.releases
            except AttributeError:
                logger.error(f"Could not find {self.image_name}. Use 'damona search' maybe")
                sys.exit(1)
            latest = r.last_release
            logger.info(
                f"No version found after {self.image_name} (e.g. fastqc:0.11.8)."
                + f" Installing latest version {latest}"
            )
            registry_name = self.image_name
            # we look only at the prefix name, not the tag. so we should get the
            # registry names from self.registry that have the prefix in common,
            # then extract the versions, and figure out the most recent.

        registry_name = self.registry.find_candidate(registry_name)
        if registry_name is None:
            logger.critical(
                f"No image found for {self.image_name}. Make sure it is correct using 'damona search' command"
            )
            sys.exit(1)

        download_name = self.registry.registry[registry_name].download

        # get metadata from the registry recipe
        info = self.registry.registry[registry_name]
        logger.info(f"{info}")

        if info.binaries:
            self.binaries = info.binaries
        else:
            logger.warning(f"No binaries field found in registry of {registry_name}")
            self.binaries = [self.input_image.guessed_executable]

        # target file is stored in output_name variable
        if output_name is None:
            output_name = registry_name.replace(":", "_") + ".img"
        # here we check whether the image or binaries are already present.
        # if md5 is already provided, and image exists, nothing to copy
        if info.md5sum:
            if os.path.exists(self.images_directory / output_name):

                md5_target = md5(self.images_directory / output_name)

                if md5_target == info.md5sum:
                    logger.info("Remote image and local image are identical, no need to download/pull again")
                    self.input_image = ImageReader(self.images_directory / output_name)
                    self.image_installed = True
                    return
        else:
            logger.warning(
                f"md5 field not found or not filled in {registry_name}."
                f"To be fixed in https://github.com/damona/damona/recipes/{self.image_name}/registry.yaml "
            )

        # now that we have the registry name, we can download the image
        logger.info("Downloading {}".format(download_name))

        pull_folder = self.images_directory / "damona_buffer"

        if self.from_url:
            # The client does not support external https link other than
            # docker, library, shub.
            cmd = f"singularity pull --dir {pull_folder} "
            if force:
                cmd += " --force "
            cmd += f"{self.from_url}/{download_name}"
            print(cmd)
            subprocess.call(cmd.split())
        else:

            if download_name.startswith("https://"):
                print(f"downloading into {pull_folder} {output_name}")

                urlretrieve(download_name, filename=str(pull_folder / output_name))
                # wget.download(download_name, str(pull_folder / output_name))

            else:  # use singularity
                Client.pull(str(download_name), name=output_name, pull_folder=pull_folder, force=force)
        logger.info(f"File {self.image_name} uploaded to {pull_folder}")

        # Read the image, checking everything is correct

        self.input_image = ImageReader(pull_folder / output_name)
        shortname = self.input_image.shortname
        try:
            logger.info(f"Copying into damona image directory: {self.images_directory}")
            self.input_image.filename.rename(self.images_directory / shortname)
            self.input_image.filename = pathlib.Path(self.images_directory / shortname)
        except FileNotFoundError:
            logger.warning("File not installed properly. Stopping")
            self.image_installed = False

        # check the md5 validity
        if info.md5sum:
            if info.md5sum != self.input_image.md5:
                logger.warning(
                    "MD5 of downloaded image does not match the expected md5 found in the "
                    f"registry of {registry_name}. The latter may be incorrect in damona and needs "
                    f"to be updated in https://github.com/damona/damona/recipes/{self.image_name}/registry.yaml "
                    "or the donwload was interrupted"
                )

        self.image_installed = True


class BiocontainersInstaller(ImageInstaller):
    """

    Using bioservices.Biocontainers, we can retrieve all tools and versions.
    We store the list once in a while in damona/biocontainers/registry.yaml

        from bioservices import Biocontainers
        b = Biocontainers()
        info = b.get_tools()
        tools = {}
        for name, versions in zip(info['name'], info['versions']):
            tools[name] = [x['meta_version'] for x in versions]

    """

    def __init__(self, image_name, binaries=None, cmd=None):
        super(BiocontainersInstaller, self).__init__()


        # get the biocontainers prefix and the name:version suffix
        prefix, suffix = image_name.split("/")

        if prefix != "biocontainers":
            logger.error(f"Biocontainers name must start with 'biocontainers/' ({prefix} provided")
            sys.exit(1)

        try:
            name, version = suffix.split(":")
            self.name = name
            self.version = version
        except ValueError as err:
            logger.error(f"Biocontainers name must be formatted as NAME:VERSION ({suffix} provided)")
            sys.exit(1)

        self.registry = Registry(biocontainers=True)

        if suffix not in self.registry.registry:
            logger.error(f"{name} not found in the biocontainers registry. Use damona search PATTERN --include-biocontainers")
            sys.exit(1)

        self.image_name = image_name
        self.images_directory = pathlib.Path(DAMONA_PATH) / "images"

        self.cmd = cmd
        self.binaries = binaries
        self.image_installed = False

    def is_valid(self):
        return True

    @requires_singularity
    def pull_image(self, output_name=None, force=False):
        """Pull and Install a biocontainer image.

        """
        self.image_installed = False

        download_name = self.image_name

        # now that we have the registry name, we can download the image
        logger.info("Downloading {}".format(self.image_name))

        pull_folder = self.images_directory / "damona_buffer"
        if output_name is None:
            output_name = self.image_name.replace("biocontainers/", "")
            output_name = output_name.replace(":", "_") + ".img"

        #
        Client.pull("docker://" + str(self.image_name), name=output_name, pull_folder=pull_folder, force=force)
        logger.info(f"File {self.image_name} uploaded to {pull_folder}")

        #
        self.input_image = ImageReader(pull_folder / output_name)

        shortname = self.input_image.shortname
        try:
            logger.info(f"Copying into damona image directory: {self.images_directory}")
            self.input_image.filename.rename(self.images_directory / shortname)
            self.input_image.filename = pathlib.Path(self.images_directory / shortname)
        except FileNotFoundError:
            logger.warning("File not installed properly. Stopping")
            self.image_installed = False

        # for the install_binaries to work, we need to set the binaries
        prefix, suffix = self.image_name.split("/")
        self.binaries = self.registry.registry[suffix].binaries



        self.image_installed = True




class BinaryInstaller:
    """Install a binary in the bin/ directory of the current environment given its image


    """
    def __init__(self, binaries, parent_image_path):
        """.. rubric:: **Constructor**

        :param list binaries: list of binaries to install
        :param str parent_image_path: the location of the images where binaries are to be found

        """
        #: instance of :class:`damona.common.ImageReader`
        self.image = ImageReader(parent_image_path)
        self.binaries = binaries

    @requires_singularity
    def install_binaries(self, force=False):
        """Install an image and its binaries

        Given the :attr:`~damona.install.BinaryInstaller.image`, we install a set of :attr:`~damona.install.BinaryInstaller.binaries` to be found in the
        image registry. If we install a binary again, no need to rewrite the command. For example,
        imagine that you installed fastqc.0.11.9 for the first time, then in the commands
        here below::

            damona install fastqc:0.11.9
            damona install fastqc:0.11.9 --force

        the second command has no effect. If we now install a new version::

            damona install fastqc:0.11.8

        The previous binary (v0.11.9) will be replaced by the new one (v0.11.8).
        The old image is kept in the images directory (it may be used in another 
        environment indeed).
        """

        env = Environ()
        bin_directory = env.get_current_env() / "bin"
        logger.info(bin_directory)

        for binary in sorted(self.binaries):
            bin_path = pathlib.Path(bin_directory) / binary

            CMD = """singularity -s exec ${{DAMONA_SINGULARITY_OPTIONS}} {} {} ${{1+"$@"}}"""
            CMD = CMD.format(f"${{DAMONA_PATH}}/images/{self.image.shortname}", binary)

            if bin_path.exists() and force is False:
                name = pathlib.Path(bin_path).name
                path = str(bin_path).rstrip(bin_path.name)
                logger.warning(
                    f"Binary {binary} exists already in {path} and was not changed. Use --force to overwrite"
                )
            else:
                # create a new binary content and save into an executable file
                with open(bin_path, "w") as fout:
                    fout.write(f"#!/bin/sh\n{CMD}")

                # update permission so that it is executable
                os.chmod(bin_path, 0o755)

                # print message
                name = pathlib.Path(bin_path).name
                path = str(bin_path).rstrip(bin_path.name)
                logger.info(f"Created binary {name} in {path}")
