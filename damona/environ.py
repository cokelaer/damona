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
"""Environments manager"""
import os
import shutil
import sys
import pathlib
import math
import tarfile
import time

from damona.common import Damona
from damona.common import BinaryReader


manager = Damona()


import colorlog

logger = colorlog.getLogger(__name__)


__all__ = ["Environ", "Environment"]


class Environment:
    """Class to handle a specific environment


    ee = environ.Environment("test1")
    ee.create_bundle("test.tar")

    """

    def __init__(self, name):
        self._init(name)

    def _init(self, name):

        self.name = name
        self.path = manager.damona_path / f"envs/{name}/"

        if self.path.exists() is False:
            logger.error(f"Environment {self.path} does not exits")
            sys.exit(1)

    def get_installed_binaries(self):
        """Return all binaries of the environment"""
        binaries = self.path.glob("bin/*")
        binaries = [x for x in binaries if x.is_dir() is False]

        return [x for x in binaries]

    def get_disk_usage(self):
        """Return virtual size of the environment if we were to
        copy/export all images"""
        binaries = self.get_installed_binaries()
        S = 0
        images = self.get_images()
        for image in images:
            try:
                if "DAMONA_PATH" not in os.environ:  # pragma: no cover
                    logger.error("You must define a DAMONA_PATH")
                    sys.exit(1)
                damona_path = os.environ["DAMONA_PATH"]
                image = image.replace("${DAMONA_PATH}", damona_path)
                S += os.path.getsize(image)
            except Exception as err:  # pragma: no cover
                print(err)
                logger.error(f"Could not check {image}")
        return S

    def get_images(self):
        binaries = self.get_installed_binaries()
        images = []
        for binary in binaries:
            br = BinaryReader(binary)
            if br.image not in images:
                images.append(br.image)
        return images

    def __repr__(self):
        N = len(self.get_installed_binaries())
        M = len(self.get_images())

        txt = f"Contains {N} binaries from {M} images."
        disk = self.get_disk_usage()
        import math

        env_size = math.ceil(disk / 1e6)

        txt += f" Disk usage is {env_size}Mb"
        return txt

    def rename(self, newname, force=False):
        if self.name == "base":
            logger.error("You cannot rename the 'base' environment")
            sys.exit(1)

        if newname in Environ().environment_names:
            logger.error(f"{newname} exists already. Please choose another name")
            sys.exit(1)

        if not force:
            logger.warning(f"You are about to rename your current {self.name} environment into {newname}")
            input("Press enter to accept this change")

        ff = pathlib.Path(self.path)
        ff.rename(self.path.parent / newname)
        # reset the path
        self._init(newname)
        logger.warning("Please restart a new shell if this is an active environment.")

    def get_current_state(self):
        images = set()
        binaries = {}
        for filename in self.get_installed_binaries():
            br = BinaryReader(filename)
            image = br.get_image()
            binaries[filename.name] = image
            images.add(image)
        return {"images": images, "binaries": binaries, "name": self.name}

    def create_bundle(self, output_name=None, exclude=None):
        if output_name is None:
            output_name = self.name

        if exclude:
            exclude = list(self.path.glob(f"bin/{exclude}"))
        else:
            exclude = []

        # all binaries
        binaries = self.get_installed_binaries()
        binaries = [x.absolute() for x in binaries if x not in exclude]
        binaries = sorted(binaries)

        # all containers
        images = [pathlib.Path(x) for x in self.get_images()]

        archive = tarfile.open(f"damona_{output_name}.tar", "w")
        for filename in binaries:
            logger.info(f"Adding {filename}")
            archive.add(filename, arcname=f"bin/{filename.name}")
        for filename in images:
            logger.info(f"Adding {filename}")
            archive.add(filename, arcname=f"images/{filename.name}")
        archive.close()

        logger.info(f"Saved environment {self.name} into damona_{output_name}.tar")

    def save_snapshot(self):

        ctime = time.asctime().replace(" ", "_")
        p = self.path / "bin" / ctime
        if not p.exists():
            p.mkdir()
        else:
            time.sleep(1)
            p.mkdir()

        filenames = [x for x in (self.path / "bin").glob("*") if not x.is_dir()]
        for filename in filenames:
            with open(filename, "r") as fin:
                data = fin.read()
                with open(p / filename.name, "w") as fout:
                    fout.write(data)


class Images:
    def __init__(self):
        self.images_dir = manager.images_directory

    def __len__(self):
        return len(list(self.files))

    def _get_images(self):
        return self.images_dir.glob("*.img")

    files = property(_get_images)

    def get_disk_usage(self, frmt="Mb"):
        env_size = sum(os.path.getsize(f) for f in self.files if os.path.isfile(f))
        if frmt == "Mb":
            return math.ceil(env_size / 1e6)
        else:
            return env_size


class Environ:
    """Class to deal with the damona environments"""

    def __init__(self):
        self.images = Images()

    @staticmethod
    def get_current_env():
        if "DAMONA_ENV" not in os.environ:
            logger.error(
                "You do not have any environment activated. Please use "
                "'damona activate ENVNAME' where ENVNAME is a valid environment"
            )
            sys.exit(1)
        else:
            return pathlib.Path(os.environ["DAMONA_ENV"])

    @staticmethod
    def get_current_env_name():
        if "DAMONA_ENV" not in os.environ:
            logger.warning(
                "You do not have any environment activated. Please use "
                "'damona activate ENVNAME' where ENVNAME is a valid environment"
            )
            # sys.exit(1)
            return None
        else:
            path = pathlib.Path(os.environ["DAMONA_ENV"])
            return path.name

    def _get_N(self):
        return len(self.environments)

    N = property(_get_N)

    def _get_envs(self):
        path_envs = manager.damona_path / "envs"
        envs = [Environment(x.name) for x in path_envs.iterdir()]
        return envs

    environments = property(_get_envs)

    def _get_env_names(self):
        envs = os.listdir(manager.environments_path)
        envs = sorted([Environment(x).name for x in envs])
        return envs

    environment_names = property(_get_env_names)

    def delete(self, env_name):

        if env_name == "base":
            logger.error("Environment 'base' is reserved and cannot not be created or deleted")
            sys.exit(1)

        env_path = manager.environments_path / env_name
        if os.path.exists(env_path) is False:
            logger.error("{} does not exists".format(env_path))
        else:
            try:
                os.rmdir(env_path)
            except OSError:
                logger.warning(
                    "Will delete all contents of {}. Although this concerns only aliases you will lose your environement".format(
                        env_path
                    )
                )
                ret = input("Are you sure you want to proceed ? (N/y)")
                if ret == "y":
                    shutil.rmtree(env_path)

    def _env_in_path(self, env_name):
        PATH = os.environ["PATH"]
        paths = PATH.split(":")
        for x in paths:
            if str(manager.damona_path / "envs" / env_name / "bin") == x:
                return True
        return False

    def activate(self, env_name=None):
        # Do not change the print statement here below. They are used by
        # damona.sh
        if env_name not in self.environment_names:
            logger.error(f"invalid environment:  {env_name}. Please use 'damona env' to get the list")
            sys.exit(1)

        if self._env_in_path(env_name) is True:
            logger.warning(f"damona environment {env_name} is already in your PATH. nothing done")
            return

        env_path = manager.environments_path / env_name
        print("    export DAMONA_ENV={};".format(env_path))
        print("export PATH={}/bin:${{PATH}}".format(env_path))
        logger.info(f"# Added damona path ({env_path}) in your PATH")

    def deactivate(self, env_name=None):
        # we deactivate the latest activated damona environment only.
        # can be called several times. If called too many times,
        # we set the main damona environment (base) as default
        PATH = os.environ["PATH"]
        paths = PATH.split(":")

        found = False  # this one is the one to deactivate (to ignore)
        newPATH = []
        for path in paths:
            # if deactivate without name, we remove the last one only
            if env_name and str(manager.damona_path / "envs" / env_name / "bin") == path:
                logger.info(f"# Found damona path ({path}), now removed from your PATH")
                found = True
            elif not env_name and f"/damona/envs/" in str(path) and not found:
                logger.info(f"# Found damona path ({path}), now removed from your PATH")
                found = True
            else:  # keep track of the DAMONA_ENV.
                newPATH.append(path)

        if found is False:
            logger.info("# no more active damona environment in your path. Use 'damona activate ENVNAME'")

        first_damona_path = [x for x in newPATH if "/damona/envs/" in x]
        if len(first_damona_path):
            first_damona_path = first_damona_path[0]
            print(f"    export DAMONA_ENV={first_damona_path};")
        else:
            print("    unset DAMONA_ENV")
        newPATH = ":".join(newPATH)
        print("export PATH={}".format(newPATH))

    def create(self, env_name, force=False):
        if env_name == "base":
            logger.critical("base is a reserved name for environment. Cannot be created")
            sys.exit(1)

        env_directory = manager.damona_path
        env_path = env_directory / "envs" / env_name
        if os.path.exists(env_path) and force is False:
            logger.critical("{} exists already".format(env_path))
            sys.exit(0)
        else:
            try:
                os.mkdir(env_path)
                os.mkdir(env_path / "bin")
                logger.info(f"Created {env_name} in {env_directory}")
                logger.info(f"Type 'damona activate {env_name}' to activate it")
            except:  # pragma: no cover
                pass  # if already created, error are caught here

    def create_from_bundle(self, env_name, bundle, force=False):
        if env_name in self.environment_names:
            logger.warning(f"{env_name} exists already.")
            if force is False:
                logger.critical(f"To recreate, you must delete it using 'damona env --delete {env_name}'")
                sys.exit(0)
            else:
                logger.warning(f"You used --force, so overwritting existing environment")

        # if it does not exsits or force is True
        self.create(env_name, force=force)

        env_directory = pathlib.Path(manager.damona_path / "envs" / env_name)

        archive = tarfile.open(bundle)
        for x in archive.getmembers():
            if x.name.startswith("bin"):  # this is a binary
                archive.extract(x, path=env_directory)
            elif x.name.startswith("images"):  # a contaier
                archive.extract(x, path=env_directory)
                from damona.common import ImageReader

                temp_image = ImageReader(env_directory / x.name)
                if temp_image.is_installed():
                    target_image = ImageReader(manager.damona_path / x.name)
                    if target_image.md5 == temp_image.md5:
                        logger.info(f"- Image {x.name} exists already with same md5sum. Skipped copy.")
                    else:
                        logger.warning(
                            f"- Image {x.name} exists already with diffrent "
                            " md5sum. This should not happen with damona images."
                            " You will need to copy manually if required"
                        )
                else:
                    logger.info(f"- Copying {x.name} into {manager.damona_path}/images")
                    temp_image.filename.rename(manager.damona_path / "images" / temp_image.filename.name)
            else:  # we should not enter here
                raise NotImplementedError

        # finally, we remove all images since they are redundant or have
        # been copied
        def rm_tree(pth):
            pth = pathlib.Path(pth)
            for child in pth.glob("*.img"):
                if child.is_file():
                    child.unlink()
                else:
                    rm_tree(child)
            pth.rmdir()

        to_delete = (env_directory / "images").absolute()
        logger.info(f"Removing temporary {to_delete} directory")
        rm_tree(env_directory / "images")

    def copy(self):
        """Copy an environment"""
        raise NotImplementedError
