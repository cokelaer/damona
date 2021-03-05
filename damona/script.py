# -*- coding: utf-8 -*-

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
""".. rubric:: Standalone application dedicated to conversion"""
import click
import click_completion
click_completion.init()
import glob
import sys
import pathlib
import os
import subprocess

from damona  import version
from damona import Damona
manager = Damona()


__all__ = ["main"]

from damona import logger
logger.level = 10



CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.group(context_settings=CONTEXT_SETTINGS)
@click.option("--level", default="INFO", 
    help="""Set level information to DEBUG, INFO, WARNING, CRITICAL, ERROR. Use e.g., "damona --level INFO command" """)
@click.version_option(version=version)
def main(level):
    """Damona is a singularity container manager to ease the deployment of
    reproducible working environments. It is to singularity container what conda
    is to packaging.

    You can create and activate a Damona environment using

    \b
        damona env --create env1
        damona activate env1

    You can install a Damona-registered image:


        damona install fastqc

    Or build and install a local image:
    \b
        damona build Singularity.test_1.0.0
        damona install test_1.0.0.img --binary-name fastqc

    Images can be built from docker:

        damona build docker://whatever

    Or install from online registry (given a URL). Once done, you can export
    your environment to another computer::

        damona export test1 --name myenv
        # on a remote computer
        damona import myenv

    """
    from damona.colors import Colors
    ##### !!!!!!!!!!!! this function cannot print anything because the damona 
    # activate command prints bash commands read by damona.sh
    #print(Colors().blue("# Welcome to Damona (Container Manager)"))
    from damona import logger
    logger.setLevel(level)


@main.command()
@click.argument('filename', required=True, type=click.STRING)
@click.option('--destination', default=None,
    help="Not implemented yet")
@click.option('--force', is_flag=True,
    help="add --force option")
def build(**kwargs): #pragma: no cover
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
    filename = kwargs['filename']
    force = kwargs['force']
    destination = kwargs['destination']

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
    elif kwargs['filename'].startswith("docker://"):
        from damona.builders import BuilderFromDocker
        builder = BuilderFromDocker()
        filename = filename.replace("docker://","")
        builder.build(filename, destination=destination, force=force)
    else: # could be a damona recipes
        logger.info("Not a docker URL, nor a local file.")


@main.command()
@click.option('--pattern', default=None, 
    help="restrict the output list keeping those with this pattern")
@click.option('--from-url', help="""download registry from remote URL. The URL must
contain a registry.txt as explained on damona.readthedocs.io. If you just type
'damona', the URL will be biomics.pasteur.fr/drylab/damona/registry.txt""") 
def list(**kwargs):
    """List all available images from Damona.

    # TODO: list in conda is the list of installed paclages. we should rename this comamnd
    # into e.g.,

     all available images:

        damona list

    List all available images available at a given URL:

        damona list --from-url https://biomics.pasteur.fr/drylab/damona/registry.txt

    Same command as above (alias) using the short name::

        damona list --from-url damona

    """
    from damona.registry import Registry
    modules = Registry(from_url=kwargs["from_url"]).get_list(pattern=kwargs['pattern'])
    print("\n".join(modules))


#TODO --rename

@main.command()
@click.option('--create', type=click.STRING,
    help="""create a new environment""")
@click.option('--delete', type=click.STRING,
    help="""Delete an existing environment""")
@click.option('--disk-usage', is_flag=True,
    help="Prints disk usage of each Damona environments")
def env(**kwargs):
    """Get information about Damona environments.

    Print the current environments and available environments:

        damona env

    Check the disk usage of each environments::

        damona env --disk-usage

    """
    logger.debug(kwargs)
    from damona import Environ
    envs = Environ()

    if kwargs['disk_usage']:
        import math
        from damona import Environ
        envs = Environ()
        #base = envs.get_current_env() + "/images/*img"
        #env_size = sum(os.path.getsize(f) for f in glob.glob(base) if os.path.isfile(f))
        N = len(envs.images)
        usage = envs.images.get_disk_usage()
        #env_size = math.ceil(env_size/1e6)
        print(f"Found {N} images: Images usage: {usage}.Mb")
    elif kwargs['create'] is None and kwargs['delete'] is None:
        print(f"There is currently one base (default) environment and {envs.N} user environments.")
        if envs.N !=0:
            for this in envs.environments:
                name = this.name
                print(f"{name} -  {this}")
        current_env = envs.get_current_env()
        logger.info("""Your current env is {}.""".format(current_env))
    elif kwargs['create'] and kwargs['delete']: # mutually exclusive
        logger.error("you cannot use --delete and --create together")
    elif kwargs['delete']:
        envs.delete(kwargs['delete'])
    elif kwargs['create']:
        envs.create(kwargs["create"])


@main.command()
@click.argument('name', required=True, type=click.STRING)
# TODO:
# @click.argument('--all', e, type=click.STRING)
def activate(**kwargs):
    """Activate a damona environment.


    The main Damona environment can be activated using 

        damona activate base

    Then, activation of a specific environment is done as :

        damona activate my_favorite_env

    """
    # logger.debug(kwargs)
    from damona import Environ
    env = Environ()
    env.activate(kwargs['name'])


@main.command()
@click.argument('name', required=False, type=click.STRING, default=None)
def deactivate(**kwargs):
    """Deactivate the current Damona environment.

    deactivate the current environement:

        damona deactivate

    """
    logger.debug(kwargs)
    from damona import Environ
    env = Environ()
    env.deactivate(kwargs['name'])


@main.command()
@click.argument('image', required=True, type=click.STRING)
@click.option('--force-image', is_flag=True)
@click.option('--force', is_flag=True)
@click.option('--force-binaries', is_flag=True)

@click.option('--from-url', help="""download image from a remote URL. The URL must
contain a registry.txt as explained on damona.readthedocs.io""") 

@click.option('--binaries', default=None, 
    help="""If not provided, we assume this is an executable singulatrity and its name is the binary name
    """)
def install(**kwargs):
    """Download and install an image and its associated binaries

    The main idea of Damona is to download and install images already built for
    you. They may be part of Damona and available on one of the sylabs.io server
    or damona website. Available images can be shown using "damona list". Such
    images are named as "name:version" and are available in the damona registry file.
    From the registry file, we can figure out from where it can be downloaded

    For instance fastqc:0.11.9 is downloaded from library://cokelaer/damona/fastqc:0.11.9
    that is on syslabs.io website.

        damona install fastqc:0.11.9

    If you omit the version, the latest version is downloaded.

        damona install fastqc

    Images for registered containers are installed together with their
    registered binaries. 

    You may have built a local image, in which case,  you may need to specify
    the version and/or binaries to be installed. If no binary is provided, we
    assume that the name of the image is the binary name. For local image, we
    use the _ charater to separate the container name and the version:

    \b
        damona install fastqc_0.4.2.img
        damona install test_0.4.2.img --binary fastqc

    Image file name must follow the naming convention NAME_[v]x.y.z[_info].img
    where the [v] character is optional and the [_info] is an optionak _
    character followed by any text. Finally, the extension can be .img or .sif

    Under Linux the DAMONA PATH is under ~/.config/damona

    Finally, you may have images online on a website. To install such image use 
    the --from-url (sse developer guide for details).


    """
    logger.debug(kwargs)

    image_path = pathlib.Path(kwargs['image']).absolute()

    force = kwargs['force']
    force_image = kwargs['force_image']
    force_binaries = kwargs['force_binaries']
    if force:
        force_image, force_binaries = True, True

    if kwargs['binaries']:
        if "," in kwargs['binaries']:
            binaries = kwargs['binaries'].split(",")
        else:
            binaries = [kwargs['binaries']]
    else:
        binaries = None

    if os.path.exists(image_path) is False:
        if kwargs['from_url']:
            url = kwargs['from_url']
            logger.info(f"Installing from online registry  (url: {url})")
        else:
            logger.info("Installing from Damona registry")
        from damona.install import RemoteImageInstaller
        p = RemoteImageInstaller(kwargs['image'], 
                from_url=kwargs['from_url'], cmd=sys.argv, binaries=binaries)
        if p.is_valid():
            p.pull_image(force=force_image)
            p.install_binaries(force=force_binaries)
        else:
            logger.critical("Something wrong with your image/binaries. See message above")
    else:
        # This install the image and associated binary/binaries
        from damona import environ
        env = environ.Environ()
        cenv = env.get_current_env()
        logger.info(f"Installing local container in {cenv}")
        from damona.install import LocalImageInstaller
        lii = LocalImageInstaller(image_path, cmd=sys.argv, binaries=binaries)
        if lii.is_valid():
            lii.install_image(force=force_image)
            lii.install_binaries(force=force_binaries)
        else:
            logger.critical("Something wrong with your image/binaries. See message above")


@main.command()
@click.option('--path', required=True,
    help="path to recipes directory where Singularity file(s) can be found")
def registry(**kwargs):
    """Developers kit (eg build registry)"""
    logger.debug(kwargs)
    from damona.registry import Registry

    if kwargs['path'] and os.path.exists(kwargs['path']):
        modules = Registry().create_registry(kwargs['path'])
    else:
        logger.critical('Please provide a valid path where to find Singulary from damona software')


@main.command()
@click.argument('name', required=True, type=click.STRING)
@click.option("--from-image", required=True)
def add_binary(**kwargs):
    """Create a binary linked to an existing image

        conda add-binary fastqc --from-image test_0.4.0.img
    """
    logger.debug(kwargs)
    raise NotImplementedError


@main.command()
@click.option("--remove", is_flag=True,
              help="--remove the binary and image orphans in all environments ")
def clean(**kwargs):
    """Remove orphan images and binaries from all environments

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

    if kwargs['remove']:
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

    if kwargs['remove']:
        for x in orphans:
            #os.remove(os.path.expanduser(x))
            logger.info(f"Removed {x}")
    else:
        logger.warning("Please use --remove to confirm that you want to remove the orphans")

@main.command()
@click.argument('pattern', required=True, type=click.STRING)
@click.option('--from-url', help="""download registry from remote URL. The URL must
contain a registry.txt as explained on damona.readthedocs.io. If you just type
'damona', the URL will be biomics.pasteur.fr/drylab/damona/registry.txt""")
def search(**kwargs):
    """Search for a pattern in damona registry.

        damona search fastqc
        damona install fastqc:0.11.9
    """
    logger.debug(kwargs)
    from damona.registry import Registry
    modules = Registry(from_url=kwargs["from_url"]).get_list(pattern=kwargs['pattern'])

    pattern = kwargs['pattern']
    for mod in modules:
        if pattern in mod:
            print(mod)



@main.command()
@click.argument('environment', required=True, type=click.STRING)
def info(**kwargs):
    """Print information about a given environement

        damona info test1

    """
    logger.debug(kwargs)
    print('coming soon')
    envname = kwargs['environment']
    from damona.environ import Environ
    manager = Environ()

    x = [ee for ee in manager.environments if ee.name == envname]
    if len(x) == 0:
        logger.error(f"Environment '{envname}' does not exist. Use 'damona env' to get the list")
        sys.exit(1)
    else:
        environ = x[0]
        print(environ)
        print("Images:")
        for item in environ.get_images():
            print(" - " + pathlib.Path(item).name)
        print("Binaries:")
        for item in sorted(environ.get_installed_binaries()):
            print(" - " + pathlib.Path(item).name)

@main.command('import')
@click.argument('name', required=True, type=click.STRING)
def my_import(**kwargs):
    """Import a Damona bundle in a DAMONA environment.

    Given images and binaries in the bundle, create an environment named after
    the bundle, save images in the main Damona image directories and created the
    binaries in the bin directory of the newly created environment
    """
    raise NotImplementedError



@main.command()
@click.argument('environment', required=True, type=click.STRING)
@click.option("--exclude", default=None,
              help="--exclude 'bowtie*' ")
@click.option("--include", default=None,
              help="--include 'bowtie*' ")
def export(**kwargs):
    """Create a bundle of a given environment.

    the following command retrieve all binaries from an environement and the
    associated images and save them into a tar ball file named after the
    environment.

        damona export test1 --exclude "bowtie*"

    This environment can be installed elsewhere later using

        damona env create --name test --from damona_test1.tar

    """
    logger.debug(kwargs)
    environment = kwargs['environment']
    exclude = kwargs['exclude']
    include = kwargs['include']

    # TODO This should be based on the binaries of the environment, not the images
    # to do so, we'll need an installed.txt file

    from damona import Environment
    envname = kwargs['environment']
    env = Environment(envname)
    env.create_bundle()

    """
    if exclude:
    if exclude:
        to_exclude = glob.glob(f"{damona_config_path}/images/{exclude}")
    else:
        to_exclude = []

    if include:
        filenames = glob.glob(f"{damona_config_path}/images/{include}")
    else:
        filenames = glob.glob(f"{damona_config_path}/images/*")

    filenames = [x for x in filenames if x not in to_exclude]
    filenames = " ".join(filenames)
    cmd = f"tar cvf damona_{environment}.tar {filenames}"
    subprocess.call(cmd.split())
    """
    logger.info(f"Saved environment into {environment}.tar")
    logger.info(f"Use this command to create a new environment: damona env --create test --from-bundle {environment}.tar")




if __name__ == "__main__": #pragma: no cover
    main()

