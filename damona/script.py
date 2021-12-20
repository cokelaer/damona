###########################################################################
# Damona is a project to manage reproducible containers                  #
#                                                                         #
# Authors: see CONTRIBUTORS.rst                                           #
# Copyright © 2020-2021  Institut Pasteur, Paris and CNRS.                     #
# See the COPYRIGHT file for details                                      #
#                                                                         #
# Damona is free software: you can redistribute it and/or modify          #
# it under the terms of the GNU General Public License as published by    #
# the Free Software Foundation, either version 3 of the License, or       #
# (at your option) any later version.                                     #
#                                                                         #
# Damona  is distributed in the hope that it will be useful,              #
# but WITHOUT ANY WARRANTY; without even the implied warranty of          #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the           #
# GNU General Public License for more details.                            #
#                                                                         #
# You should have received a copy of the GNU General Public License       #
# along with this program (COPYING file).                                 #
# If not, see <http://www.gnu.org/licenses/>.                             #
###########################################################################
""".. rubric:: Standalone application dedicated to Damona"""
import click
import time
import sys
import pathlib
import os


from damona import version
from damona import Damona
from damona import Environ

from damona.registry import ImageName, Registry, Software

manager = Damona()


__all__ = ["main", "build"]

from damona import logger

logger.level = 10


CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.group(context_settings=CONTEXT_SETTINGS)
@click.option(
    "--level",
    default="INFO",
    help="""Set level information to DEBUG, INFO, WARNING, CRITICAL, ERROR. Use e.g., "damona --level INFO command" """,
)
@click.version_option(version=version)
def main(level):
    """

    Damona is an environment manager for singularity containers.

    It is to singularity container what conda is to packaging.

    The default environment is called 'base'. You can create and activate
    a new environment as follows

    \b
        damona env --create TEST
        damona activate TEST

    Once an environment is activated, you can install a Damona-registered image
    (and its registered binaries)

        damona install fastqc

    \b
    More information on https://damona.readthedocs.io.
    Please report issues on https://github.com/cokelaer/damona
    Contact: Thomas Cokelaer at pasteur dot fr

    "Make everything as simple as possible, but not simpler." -- Albert Einstein
    """
    from damona.colors import Colors

    ######################## !!!!!!!!!!!! ####################
    # this function cannot print anything because the damona
    # activate command prints bash commands read by damona.sh
    ######################## !!!!!!!!!!!! ####################
    from damona import logger

    logger.setLevel(level)


@main.command(hidden=True)
@click.argument("filename", required=True, type=click.STRING)
@click.option("--destination", default=None, help="Not implemented yet")
@click.option("--force", is_flag=True, help="add --force option")
def build(**kwargs):  # pragma: no cover
    """Build a container from dockerhub, singularity file or damona recipes.

    Note that to use this command, you must have sudo permissions.
    If not, you will need to download existing images. See the "damona install
    command".

    You can build a singularity image from a local singularity file. Note that
    your Singulary recipes must follow the naming convention
    Singularity.NAME_x,y,z

    \b
        # a local recipes (recipes must have a version)
        damona build Singularity.salmon_1.3.0

    You may build an image from a singularity recipes to be found in Damona
    itself. In such case, the name and version are enough. Siuch recipes can be
    listed using "damona list"

        damona build salmon:1.3.0

    You may also build image from a docker image to be found on docker hub:

    \b
        damona build docker://biocontainers/bowtie2:v2.4.1_cv1
        damona build docker://kapeel/hisat2

    TO be implemented: from singularity hub or sylabs.io

    """
    logger.debug(kwargs)
    filename = kwargs["filename"]
    force = kwargs["force"]
    destination = kwargs["destination"]

    if destination:
        if destination.endswith(".img") is False:
            logger.warning("You should end your image with the .img extension")
        if "_" not in destination:
            logger.warning("You should name your image as NAME_x.y.z")

    if os.path.exists(filename) and os.path.isdir(filename) is False:
        # TODO check that it starts with Singularity
        # local recipes ?
        from damona.builders import BuilderFromSingularityRecipe

        builder = BuilderFromSingularityRecipe()
        builder.build(filename, destination=destination, force=force)
    elif kwargs["filename"].startswith("docker://"):
        from damona.builders import BuilderFromDocker

        builder = BuilderFromDocker()
        filename = filename.replace("docker://", "")
        builder.build(filename, destination=destination, force=force)
    else:  # could be a damona recipes
        logger.info("Not a docker URL, nor a local file.")


@main.command()
@click.option("--create", type=click.STRING, help="""create a new environment""")
@click.option("--delete", type=click.STRING, help="""Delete an existing environment""")
@click.option("--rename", type=click.STRING, help="""Rename an existing environment""")
@click.option("--new-name", type=click.STRING, default="", help="""The new environment name (use with --rename) only""")
@click.option("--disk-usage", is_flag=True, help="Prints disk usage of each Damona environments")
@click.option("--from-bundle", type=click.STRING, help="a bundle file create with 'damona export' command")
@click.option(
    "--force",
    is_flag=True,
    help="""When creating an environment with --from-bundle, rewrite binaries and
images even though the environment exists.""",
)
def env(**kwargs):
    """Create/Delete/Rename environments here.

    Print information about current environments:

        damona env

    Check the disk usage of each environments::

        damona env --disk-usage

    You can also create an environment and install a saved on in it:

    \b
        damona export test1
        damona env --create copy_test1 --from-bundle damona_test1.tar

    """
    envs = Environ()

    if kwargs["disk_usage"]:
        envs = Environ()
        N = len(envs.images)
        usage = envs.images.get_disk_usage()
        click.echo(f"Found {N} images: Images usage: {usage}.Mb")
    elif kwargs["create"] is None and kwargs["delete"] is None and kwargs["rename"] is None:
        click.secho(f"There are currently {envs.N} Damona environments:\n", bold=True)
        if envs.N != 0:
            for this in envs.environments:
                name = this.name
                click.echo(click.style(f"{name}", bold=True) + click.style(f" -  {this}"))
        current_env = envs.get_current_env_name()
        click.secho(f"\nYour current env is '{current_env}'.", bold=True)
    elif kwargs["create"] and kwargs["delete"]:  # mutually exclusive
        logger.error("you cannot use --delete and --create together")
        sys.exit(1)
    elif kwargs["create"] and kwargs["rename"]:  # mutually exclusive
        logger.error("you cannot use --delete and --rename together")
        sys.exit(1)
    elif kwargs["rename"] and kwargs["delete"]:  # mutually exclusive
        logger.error("you cannot use --delete and --rename together")
        sys.exyyit(1)

    elif kwargs["delete"]:
        envs.delete(kwargs["delete"])
    elif kwargs["create"]:
        if kwargs["from_bundle"]:
            envs.create_from_bundle(kwargs["create"], bundle=kwargs["from_bundle"], force=kwargs["force"])
        else:
            envs.create(kwargs["create"])
    elif kwargs["rename"]:
        if kwargs["new_name"] == "":
            logger.error("If you use --rename, you must provide a new name with --new-name")
            sys.exit(1)
        from damona.environ import Environment

        env = Environment(kwargs["rename"])
        env.rename(kwargs["new_name"], force=kwargs["force"])


@main.command()
@click.argument("name", required=True, type=click.STRING)
def activate(**kwargs):
    """Activate a damona environment.

    The main Damona environment can be activated using

        damona activate base

    Then, activation of a specific environment is done as :

        damona activate my_favorite_env

    """
    # DO NOT PRINT ANYTHING HERE OTHERWISE YOU'LL BREADK
    # DAMONA BASH EXPORT.If yo do, use # as commented text
    click.echo("#Inside main command")
    from damona import Environ

    env = Environ()
    env.activate(kwargs["name"])


@main.command()
@click.argument("name", required=False, type=click.STRING, default=None)
def deactivate(**kwargs):
    """Deactivate the current Damona environment.

    deactivate the current environment::

        damona deactivate

    """
    # DO NOT PRINT ANYTHING HERE OTHERWISE YOU'LL BREADK
    # DAMONA BASH EXPORT.If yo do, use # as commented text
    from damona import Environ

    env = Environ()
    env.deactivate(kwargs["name"])


@main.command()
@click.argument("image", required=True, type=click.STRING)
@click.option("--force-image", is_flag=True, help="Replaces existing image.")
@click.option("--force", is_flag=True, help="Replaces images and binaries.")
@click.option("--force-binaries", is_flag=True, help="Replace binaries.")
@click.option(
    "--url",
    help="""download image from a remote URL. The URL must
  contain a registry.txt as explained on https://damona.readthedocs.io""",
)
@click.option(
    "--binaries",
    default=None,
    help="""If not provided, we assume this is an executable singulatrity and its name is the binary name
    """,
)
def install(**kwargs):
    """Download and install an image and its binaries.

    An image has a name and a version and can be installed as:

        damona install NAME:version

    If the version is omitted, the latest version is installed. Therefore, the
    following two commands are equivalent if 0.11.9 is the latest version available:

    \b
        damona install fastqc
        damona install fastqc:0.11.9

    You may also install a local image. In such case, you must name your
    image with a version (e.g. fastqc_0.11.9.img). We assume that name of
    the image is the binary name, however, binaries can be set manually:

    \b
        damona install fastqc_0.4.2.img
        damona install test_0.4.2.img --binary fastqc

    By convention, images must follow the pattern NAME_[v]x.y.z[_info].img
    where the [v] character is optional and the [_info] is an optional _
    character followed by any text. Finally, the extension can be .img or .sif

    Images are installed in the ~/.config/damona/images directory. It is the
    DAMONA_PATH environment variable. Therefore, you can redefine this variable
    to install images elsewhere.

    Finally, you may have images online on a website. To install such images, use
    the --url (sse developer guide for details).
    """
    logger.debug(kwargs)

    from damona import environ

    env = environ.Environ()
    cenv = env.get_current_env()

    # url
    url = kwargs.get("from_url", None)

    image_path = pathlib.Path(kwargs["image"]).absolute()

    force_image = kwargs["force_image"]
    force_binaries = kwargs["force_binaries"]

    if kwargs["force"]:
        force_image, force_binaries = True, True

    if kwargs["binaries"]:
        if "," in kwargs["binaries"]:
            binaries = kwargs["binaries"].split(",")
        else:
            binaries = [kwargs["binaries"]]
    else:
        binaries = None

    if os.path.exists(image_path) is False:
        if kwargs["url"]:
            url = kwargs["url"]
            logger.info(f"Installing from online registry  (url: {url})")
        else:
            logger.info("Installing from Damona registry")
        from damona.install import RemoteImageInstaller

        p = RemoteImageInstaller(kwargs["image"], from_url=kwargs["url"], cmd=sys.argv, binaries=binaries)
        if p.is_valid():
            p.pull_image(force=force_image)
            p.install_binaries(force=force_binaries)
            with open(cenv / "history.log", "a+") as fout:
                cmd = " ".join(["damona"] + sys.argv[1:])
                fout.write(f"\n{time.asctime()}: {cmd}")
        else:
            logger.critical("Something wrong with your image/binaries. See message above")
    else:
        # This install the image and associated binary/binaries
        logger.info(f"Installing local container in {cenv}")
        from damona.install import LocalImageInstaller

        lii = LocalImageInstaller(image_path, cmd=sys.argv, binaries=binaries)
        if lii.is_valid():
            lii.install_image(force=force_image)
            lii.install_binaries(force=force_binaries)
            with open(cenv / "history.log", "a+") as fout:
                cmd = " ".join(["damona"] + sys.argv[1:])
                fout.write(f"\n{time.asctime()}: {cmd}")
        else:
            logger.critical("Something wrong with your image/binaries. See message above")


@main.command()
@click.argument("--image", type=click.STRING)
@click.option(
    "--binaries",
    help="""If not provided, we assume this is an executable singulatrity and its name is the binary name
    """,
)
@click.option("--force", is_flag=True, help="force the removal of binaries or images")
def remove(**kwargs):
    """Remove images or binaries from an environment.

    If an image (and its binaries) is removed from an environment,
    it may not be removed from DAMONA if it is used in other environments.

    However, all binaries related to this image will be altered. They will be removed
    if not linked to an image anymore, or a previous binary related to another environment
    may be activated back..
    """
    logger.warning("Not implemented")
    pass


'''
@main.command()
@click.argument('name', required=True, type=click.STRING)
@click.option("--from-image", required=True)
@click.option("--env", required=True)
def add_binary(**kwargs):
    """Create a binary linked to an existing image in a specfici environment

        conda add-binary fastqc --from-image test_0.4.0.img --env ENVNAME
    """
    logger.debug(kwargs)
    raise NotImplementedError
    #TODO check that env exists
    env = kwargs['env']
    if env not in manager.environment_names:
        logger.error(f"Environment {env} not found. Check valid names using 'damona env'")
        sys.exit()
    raise NotImplementedError
'''


@main.command()
@click.option("--remove", is_flag=True, help="--remove the binary and image orphans in all environments ")
def clean(**kwargs):
    """Remove orphan images and binaries from all environments.

    This commnd finds images that have no more binary in any environment.
    This may happen with prior version of a given binary.

    Note that if you want to remove an environmnt, just delete it or use:

    conda env --delete NAME
    """
    logger.debug(kwargs)
    from damona import Damona

    dmn = Damona()

    # First we deal with orphans from the binaries directories
    orphans = dmn.find_orphan_binaries()
    if len(orphans) == 0:
        logger.info("No orphans binary found")

    if kwargs["remove"]:
        for x in orphans:
            os.remove(os.path.expanduser(x))
            logger.info(f"Removed {x}")
    else:
        logger.warning("Please use --remove to confirm that you want to remove the orphans")

    # Second, we find images that have no more binaries
    orphans = dmn.find_orphan_images()
    if len(orphans) == 0:
        logger.info("No orphan images found")
    else:
        logger.info(f"Found {len(orphans)} orphans.")

    if kwargs["remove"]:
        for x in orphans:
            answer = input(f"You are going to delete this image: {x}. Are you sure ? (yes/no)")
            if answer == "yes":
                os.remove(os.path.expanduser(x))
                logger.info(f"Removed {x}")
            else:
                logger.info(f"skipped deletion of {x}")
    else:
        logger.warning("Please use --remove to confirm that you want to remove the orphans")


@main.command()
@click.argument("pattern", required=True, type=click.STRING)
@click.option("--images-only", is_flag=True, default=False, help="Show images only")
@click.option("--binaries-only", is_flag=True, default=False, help="Show binaries only")
@click.option(
    "--url",
    help="""Set the online registry file to search for a
given container. See damona.readthedocs.io for in formation on how to write this
file . Example is available on https://biomics.pasteur.fr/salsa/damona/registry.txt""",
)
def search(**kwargs):
    """Search for a container or binary.

    By default, this command introspect the official Damona registry (based on registry files):

        damona search fastqc

    If you want to list all software and their versions, just type:

        damona search "*"

    One can also search in an online registry:

        damona search fastqc --url https://biomics.pasteur.fr/salsa/damona/registry.txt

    You may define aliases to URLs in your ~/.config/damona/damona.cfg file to
    make it easier:

        damona search fastqc --url damona

    """
    from damona.registry import Registry

    url = kwargs.get("url", None)

    if kwargs["pattern"] == "*":
        pattern = None
    else:
        pattern = kwargs["pattern"]

    if not kwargs["binaries_only"]:
        click.echo(f"Pattern '{pattern}' found in these releases:")
        modules = Registry(from_url=url).get_list(pattern=pattern)
        for mod in modules:
            click.echo(f" - {mod}")

    if not kwargs["images_only"]:
        click.echo(f"Pattern '{pattern}' found in these releases/binaries:")
        modules = Registry(from_url=url).get_binaries(pattern=pattern)
        for k in sorted(modules.keys()):
            v = modules[k]
            click.echo(f" - {k}: {v}")


@main.command()
@click.argument("environment", required=True, type=click.STRING)
def info(**kwargs):
    """Print information about a given environment.

        The default environment is called 'base'.
    b
            damona info base
            damona info test1

        Images abd binaries available are shown
    """
    logger.debug(kwargs)
    envname = kwargs["environment"]
    from damona.environ import Environ

    manager = Environ()

    x = [ee for ee in manager.environments if ee.name == envname]
    if len(x) == 0:
        logger.error(f"Environment '{envname}' does not exist. Use 'damona env' to get the list")
        sys.exit(1)
    else:
        environ = x[0]
        click.echo(environ)
        click.echo("Images:")
        for item in sorted(environ.get_images()):
            click.echo(" - " + pathlib.Path(item).name)
        click.echo("Binaries:")
        for item in sorted(environ.get_installed_binaries()):
            click.echo(" - " + pathlib.Path(item).name)


@main.command()
@click.argument("environment", required=True, type=click.STRING)
@click.option("--exclude", default=None, help="--exclude 'bowtie*' ")
def export(**kwargs):
    """Create a bundle of a given environment.

    the following command copies all binaries from an environment and their
    associated images into a tar ball file named after the
    environment.

        damona export test1 --exclude "bowtie*"

    This create a bundle named damona_test1.tar. You can then create a new
    environment starting from this bundle:

        damona env --create TEST1 --from-bundle damona_test1.tar

    """
    logger.debug(kwargs)
    environment = kwargs["environment"]
    exclude = kwargs["exclude"]

    # TODO This should be based on the binaries of the environment, not the images
    # to do so, we'll need an installed.txt file

    from damona import Environment

    envname = kwargs["environment"]
    env = Environment(envname)
    env.create_bundle(exclude=exclude)
    logger.info(f"Saved environment into {environment}.tar")
    logger.info(
        f"Use this command to create a new environment: damona env --create test --from-bundle {environment}.tar"
    )


@main.command(hidden=True)
@click.argument("filename", required=True)
@click.option(
    "--token",
    default=None,
    help="""A valid zenodo (or sandbox zenodo) token.
You can set the token in your home/.config/damona/damona.cfg that looks
like

\b
[general]
quiet=False

\b
[urls]
damona=https://biomics.pasteur.fr/salsa/damona/registry.txt
\b
[zenodo]
token=APmm6p...
orcid=0000-0001-...
affiliation=Your Institute
name=Surname, firstname
\b
[sandbox.zenodo]
token=FFmbAE...
orcid=0000-0001-...


""",
)
@click.option("--mode", default="sandbox.zenodo", help="mode can be either 'zenodo' or 'sandbox.zenodo'")
def zenodo_upload(**kwargs):  # pragma: no cover
    """Upload a singularity file to Zenodo. FOR DEVELOPERS ONLY

    This command is for developers of the DAMONA project only.

    The sandbox.zenodo is a sandbox where you can try to upload a new singularity file.

        damona zenodo-upload file_1.0.0.img --mode sandbox.zenodo

    Once done and happy with the results, you can upload to Zenodo itself once and for all:

        damona zenodo-upload file_2.0.0.img --mode sandbox.zenodo

    If no registry.yaml is found in the local directory, it is created.
    Otherwise, it is updated. The changes are also printed on the stdout.

    """
    from damona.zenodo import Zenodo

    token = kwargs["token"]
    mode = kwargs["mode"]
    filename = kwargs["filename"]

    #
    z = Zenodo(mode, token)
    logger.info(f"Uploading to {mode}")
    z._upload(filename)


@main.command()
def stats(**kwargs):
    """Get information about Damona images and binaries

    Just type:

        damona stats

    """
    from damona import admin

    admin.stats()


if __name__ == "__main__":  # pragma: no cover
    main()
