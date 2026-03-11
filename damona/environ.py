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
import math
import os
import pathlib
import shutil
import sys
import tarfile

from tqdm import tqdm

from damona.common import BinaryReader, Damona

manager = Damona()


import colorlog

logger = colorlog.getLogger(__name__)


__all__ = ["Environ", "Environment"]


class Environment:
    """Class to handle a specific environment given its name

    ::

        from damona import Environment
        ee = Environment("test1")
        ee.create_bundle("test.tar")
        ee.create_yaml("test.yaml")

    """

    def __init__(self, name):
        """.. rubric:: **Constructor**

        :param str name: the name of the environment
        """
        self._init(name)

    def _init(self, name):
        self.name = name
        self.path = manager.damona_path / f"envs/{name}/"

        if self.path.exists() is False:
            logger.error(f"Environment {self.path} does not exists")
            sys.exit(1)

    def get_installed_binaries(self):
        """Return all binaries of the environment"""
        binaries = self.path.glob("bin/*")
        binaries = [x for x in binaries if x.is_dir() is False]

        return [x for x in binaries]

    def __contains__(self, name):
        """Return ``True`` if a binary named *name* is installed in this environment.

        :param str name: The binary name to look for.
        :rtype: bool
        """
        binaries = [x.name for x in self.get_installed_binaries()]
        return name in binaries

    def get_disk_usage(self):
        """Return virtual size of the environment if we were to
        copy/export all images"""
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
        """Return list of singularity images used by the environment"""
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
        """Rename an environment.

        Note that the *base* environment cannot be renamed
        """
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
        """Return dictionary with statistics about the environment

        It includes the number of binariesm images and name of the
        environment for now.
        """
        images = set()
        binaries = {}
        for filename in self.get_installed_binaries():
            br = BinaryReader(filename)
            image = br.get_image()
            binaries[filename.name] = image
            images.add(image)
        return {"images": images, "binaries": binaries, "name": self.name}

    def create_bundle(self, output_name=None):
        """Create a bundle with all images and binaries used by the environment.

        :param str output_name: if provided this will be the output filename
        :return: the name of the bundle. If output_name is None, set to damona_ENVNAME.tar
        """
        if output_name is None:
            output_name = f"damona_{self.name}.tar"

        # for later maybe
        exclude = []

        # all binaries
        binaries = self.get_installed_binaries()
        binaries = [x.absolute() for x in binaries if x not in exclude]
        binaries = sorted(binaries)

        # all containers
        images = [pathlib.Path(x) for x in self.get_images()]

        archive = tarfile.open(output_name, "w")
        for filename in binaries:
            logger.info(f"Adding {filename}")
            archive.add(filename, arcname=f"bin/{filename.name}")
        for filename in images:
            logger.info(f"Adding {filename}")
            archive.add(filename, arcname=f"images/{filename.name}")
        archive.close()

        logger.info(f"Saved environment {self.name} into {output_name}")
        return output_name

    def create_yaml(self, output_name=None):
        """Export the environment as a YAML file.

        The YAML file lists the images and binaries that make up this
        environment and can later be used to recreate it with
        :meth:`~damona.environ.Environ.create_from_yaml`.

        :param str output_name: Path of the output file.  Defaults to
            ``damona_<name>.yaml`` in the current working directory.
        :returns: Nothing.  The file is written to disk.
        """
        if output_name is None:
            output_name = f"damona_{self.name}.yaml"

        images = [pathlib.Path(x) for x in self.get_images()]

        with open(output_name, "w") as fout:
            fout.write(f"name: {self.name}\n")
            fout.write(f"\nimages:\n")

            for image in images:
                fout.write(f"- {image.name}\n")

            fout.write(f"\nbinaries:\n")

            binaries = self.get_installed_binaries()
            binaries = [x.absolute() for x in binaries]
            binaries = sorted(binaries)

            for binary in binaries:
                bininst = BinaryReader(binary)
                fout.write(f"- {binary.name} from {bininst.get_image()}\n")


class YamlEnv:
    """Parse a YAML environment file produced by :meth:`Environment.create_yaml`.

    The file is expected to follow the format::

        name: myenv

        images:
        - fastqc_0.11.9.img

        binaries:
        - fastqc from fastqc:0.11.9

    After parsing, the instance exposes :attr:`name`, :attr:`images`, and
    :attr:`binaries` attributes.
    """

    def __init__(self, filename):
        """.. rubric:: **Constructor**

        :param str filename: Path to the YAML environment file to parse.
        """
        self.name = None
        self.binaries = []
        self.images = []

        with open(filename, "r") as fin:
            for line in fin.readlines():
                if line.startswith("name:"):
                    self.name = line.split(":")[1].strip()

                elif line.startswith("-") and " from " in line:
                    line = line.replace("- ", "").strip()
                    self.binaries.append(line)
                elif line.startswith("-") and "from" not in line:
                    line = line.replace("- ", "").strip()
                    self.images.append(line)


class Images:
    """Collection of all Singularity image files stored in the Damona images directory.

    ::

        from damona.environ import Images
        imgs = Images()
        print(len(imgs))
        for f in imgs.files:
            print(f)
    """

    def __init__(self):
        """.. rubric:: **Constructor**

        Initialises the collection by pointing at the global Damona images
        directory (``$DAMONA_PATH/images``).
        """
        self.images_dir = manager.images_directory

    def __len__(self):
        """Return the number of ``.img`` files in the images directory."""
        return len(list(self.files))

    def _get_images(self):
        return self.images_dir.glob("*.img")

    files = property(_get_images)

    def get_disk_usage(self, frmt="Mb"):
        """Return the total disk space occupied by all images.

        :param str frmt: ``"Mb"`` (default) returns megabytes (ceiling);
            any other value returns raw bytes.
        :returns: Disk usage in the requested unit.
        :rtype: int
        """
        env_size = sum(os.path.getsize(f) for f in self.files if os.path.isfile(f))
        if frmt == "Mb":
            return math.ceil(env_size / 1e6)
        else:
            return env_size


class Environ:
    """Manager for the collection of all Damona environments.

    An *environment* is a directory under ``$DAMONA_PATH/envs/`` that contains
    a ``bin/`` sub-directory with shell-wrapper scripts (binary aliases).

    ::

        from damona import Environ
        env = Environ()
        print(env.environment_names)
        env.create("myenv")
        env.activate("myenv")
    """

    def __init__(self):
        """.. rubric:: **Constructor**

        Sets up access to the shared :class:`Images` collection.
        """
        self.images = Images()

    @staticmethod
    def get_current_env():
        """Return the path of the currently active Damona environment.

        Reads the ``DAMONA_ENV`` environment variable.  Exits with an error
        message when no environment is active.

        :returns: Path to the active environment directory.
        :rtype: pathlib.Path
        :raises SystemExit: When ``DAMONA_ENV`` is not set.
        """
        if "DAMONA_ENV" not in os.environ:  # pragma: no cover
            logger.error(
                "You do not have any environment activated. Please use "
                "'damona activate ENVNAME' where ENVNAME is a valid environment"
            )
            sys.exit(1)
        else:
            return pathlib.Path(os.environ["DAMONA_ENV"])

    @staticmethod
    def get_current_env_name(warning=True):
        """Return the name of the currently active environment, or ``None``.

        :param bool warning: If ``True`` (default) a warning is logged when no
            environment is active.
        :returns: The environment name string, or ``None`` when no environment
            is active.
        :rtype: str or None
        """
        if "DAMONA_ENV" not in os.environ:
            if warning:
                logger.warning(
                    "You do not have any environment activated. Please use "
                    "'damona activate ENVNAME' where ENVNAME is a valid environment"
                )
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

    def delete(self, env_name, force=False):
        """Delete an environment and all of its binary aliases.

        The special **base** environment cannot be deleted.  If the environment
        directory is not empty the user is asked for confirmation unless
        *force* is ``True``.

        :param str env_name: Name of the environment to delete.
        :param bool force: Skip the confirmation prompt and delete immediately
            (default ``False``).
        :raises SystemExit: When attempting to delete the *base* environment.
        """
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
                if not force:
                    logger.warning(
                        f"Will delete all contents of {env_path}. Although this concerns only aliases you will lose your environement"
                    )
                else:
                    logger.warning(f"Deleting environment {env_path} since you used --force")

                if force:
                    shutil.rmtree(env_path)
                else:
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

    def _detect_shell(self):
        """Detect the current shell by inspecting the parent process name.

        Uses 'ps' to read the parent process name, which is reliable when Python
        is invoked from a shell wrapper function (bash, zsh, or fish).
        Falls back to the $SHELL environment variable if ps detection fails.
        Returns the shell name ('bash', 'zsh', or 'fish'), or an empty string
        if the shell cannot be determined.
        """
        import subprocess

        try:
            ppid = os.getppid()
            shell = subprocess.check_output(["ps", "-p", str(ppid), "-o", "comm="], text=True).strip()
            # Login shells may appear as "-bash" or "-zsh"
            if shell.startswith("-"):
                shell = shell[1:]
            if shell in ("bash", "zsh", "fish"):
                return shell
        except Exception:
            pass

        # Fallback: parse $SHELL (set by the system/login process)
        shell_path = os.environ.get("SHELL", "")
        if shell_path:
            shell_name = os.path.basename(shell_path)
            if shell_name in ("bash", "zsh", "fish"):
                return shell_name

        return ""

    def _is_fish_shell(self):
        return self._detect_shell() == "fish"

    def _is_bash_shell(self):
        return self._detect_shell() == "bash"

    def _is_zsh_shell(self):
        return self._detect_shell() == "zsh"

    def activate(self, env_name=None):
        """Print the shell commands needed to activate *env_name*.

        The output is intended to be *eval*-ed by the Damona shell wrapper
        (``damona.sh`` / ``damona.zsh`` / ``damona.fish``).  The commands
        export ``DAMONA_ENV`` and prepend the environment's ``bin/`` directory
        to ``PATH``.

        :param str env_name: Name of the environment to activate.
        :raises SystemExit: When *env_name* is not a valid environment or the
            current shell cannot be determined.
        """
        # Do not change the print statement here below. They are used by
        # damona.sh
        if env_name not in self.environment_names:
            logger.error(f"invalid environment:  {env_name}. Please use 'damona env' to get the list")
            sys.exit(1)

        if self._env_in_path(env_name) is True:
            logger.warning(f"damona environment {env_name} is already in your PATH. nothing done")
            return

        env_path = manager.environments_path / env_name

        if self._is_fish_shell():
            print(f"set -gx DAMONA_ENV {env_path}")
            print(f"set -gx PATH {env_path}/bin $PATH")
        elif self._is_bash_shell():
            print(f"   export DAMONA_ENV={env_path};")
            print("    export PATH={}/bin:${{PATH}}".format(env_path))
        elif self._is_zsh_shell():
            print(f"   export DAMONA_ENV={env_path};")
            print("    export PATH={}/bin:${{PATH}}".format(env_path))
        else:
            shell = self._detect_shell()
            logger.error(
                f"Could not determine your shell type (detected: '{shell}'). "
                "Please source the damona shell script for your shell. "
                "For bash add 'source ~/.config/damona/damona.sh' to your ~/.bashrc. "
                "For zsh add 'source ~/.config/damona/damona.zsh' to your ~/.zshrc. "
                "For fish add 'source ~/.config/damona/damona.fish' to your ~/.config/fish/config.fish"
            )
            sys.exit(1)
        logger.info(f"# Added damona path ({env_path}) in your PATH")

    def deactivate(self, env_name=None):
        """Print the shell commands needed to deactivate a Damona environment.

        When *env_name* is given, that specific environment is removed from
        ``PATH``.  When omitted, the most recently activated Damona environment
        is removed (Last-In-First-Out).  The output is intended to be
        *eval*-ed by the Damona shell wrapper.

        :param str env_name: Name of the environment to deactivate, or
            ``None`` to deactivate the most recent one.
        """
        # we deactivate the latest activated damona environment only.
        # can be called several times. If called too many times,
        # we set the main damona environment (base) as default
        PATH = os.environ["PATH"]
        paths = PATH.split(":")

        found = False  # this one is the one to deactivate (to ignore)
        removed_path = None  # track the path being removed from PATH
        newPATH = []
        for path in paths:
            # if deactivate without name, we remove the last one only
            if env_name and str(manager.damona_path / "envs" / env_name / "bin") == path:
                logger.info(f"# Found damona path ({path}), to be removed from your PATH")
                found = True
                removed_path = path
            elif not env_name and "/damona/envs/" in str(path) and not found:
                logger.info(f"# Found a damona path ({path}), to be removed from your PATH")
                found = True
                removed_path = path
            else:  # keep track of other paths.
                newPATH.append(path)

        if found is False:
            logger.info("# no more active damona environment in your path. Use 'damona activate ENVNAME'")

        damona_paths = [x for x in newPATH if "/damona/envs/" in x]
        if len(damona_paths):
            # in theory, there must be a /bin at the end of the path;
            # we should get rid of it
            first_damona_path = pathlib.Path(damona_paths[0])
            assert first_damona_path.name == "bin", "found a damona path with name different from 'bin'"
            first_damona_path = str(first_damona_path.parent)

            if self._is_fish_shell():
                print(f"set -gx DAMONA_ENV {first_damona_path}")
            else:
                print(f"    export DAMONA_ENV={first_damona_path};")
        else:
            if self._is_fish_shell():
                print("set -e DAMONA_ENV")
            else:
                print("    unset DAMONA_ENV")

        if self._is_fish_shell():
            # Remove only the specific deactivated path from PATH,
            # preserving any other entries (non-damona paths the user may have).
            if removed_path:
                print(f"set -gx PATH (string match -v -- '{removed_path}' $PATH)")
        else:
            newPATH = ":".join(newPATH)
            print("export PATH={}".format(newPATH))

    def create(self, env_name, force=False):
        """Create a new empty environment.

        Creates the directory ``$DAMONA_PATH/envs/<env_name>/bin/``.  The
        special name **base** is reserved and cannot be created.

        :param str env_name: Name for the new environment.
        :param bool force: Overwrite if it already exists (default ``False``).
        :raises SystemExit: When *env_name* is ``"base"`` or when the
            environment already exists and *force* is ``False``.
        """
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

    def create_from_yaml(self, env_name, yaml, force=False):
        """Create and populate an environment from a YAML export file.

        Reads a YAML file previously created by :meth:`Environment.create_yaml`
        and re-downloads all referenced images before re-creating the binary
        aliases.

        :param str env_name: Name of the environment to create.
        :param str yaml: Path to the ``.yaml`` file produced by
            :meth:`~damona.environ.Environment.create_yaml`.
        :param bool force: Overwrite an existing environment with the same
            name (default ``False``).
        :raises SystemExit: When the environment already exists and *force* is
            ``False``.
        """
        if env_name in self.environment_names:
            logger.warning(f"{env_name} exists already.")
            if force is False:
                logger.critical(f"To recreate, you must delete it using 'damona delete {env_name}'")
                sys.exit(0)
            else:
                logger.warning("You used --force, so overwritting existing environment")

        env_directory = pathlib.Path(manager.damona_path / "envs" / env_name)

        from damona.environ import YamlEnv

        ye = YamlEnv(yaml)
        # ye.name is not used for now, supposibly, it already exists, so we require a user input

        self.create(env_name, force=force)

        for image in tqdm(ye.images):
            # local import to avoid circular import
            from damona.install import RemoteImageInstaller

            # replace all _ with :
            image = image.rsplit(".", 1)[0].replace("_", ":")

            # and replace : with _ except last one
            image = image.replace(":", "_", image.count(":") - 1)

            rii = RemoteImageInstaller(image)
            rii.pull_image(force=True)

        for binary in tqdm(ye.binaries):
            # local import to avoid circular import
            from damona.install import BinaryInstaller

            binary, image = binary.split(" from ")
            binary = binary.strip()
            image = image.strip()
            image += ".img"
            bi = BinaryInstaller([binary], image, env_name)
            bi.install_binaries()

    def create_from_bundle(self, env_name, bundle, force=False):
        """Create and populate an environment from a bundle archive.

        A *bundle* is a ``.tar`` file previously created by
        :meth:`Environment.create_bundle`.  It contains all binary aliases
        and the associated Singularity image files.

        :param str env_name: Name of the environment to create.
        :param str bundle: Path to the ``.tar`` bundle file.
        :param bool force: Overwrite an existing environment with the same
            name (default ``False``).
        :raises SystemExit: When the environment already exists and *force* is
            ``False``.
        """
        if env_name in self.environment_names:
            logger.warning(f"{env_name} exists already.")
            if force is False:
                logger.critical(f"To recreate, you must delete it using 'damona delete {env_name}'")
                sys.exit(0)
            else:
                logger.warning("You used --force, so overwritting existing environment")

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
