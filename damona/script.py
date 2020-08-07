# -*- coding: utf-8 -*-

###########################################################################
# Damona is a project to provide reproducible containers                  #
#                                                                         #
# Authors: see CONTRIBUTORS.rst                                           #
# Copyright © 2020  Institut Pasteur, Paris and CNRS.                     #
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
import os
import glob
import json
import sys
import colorlog
import textwrap
import subprocess
import click
from damona  import version,  images_directory
import pathlib

__all__ = ["main"]

from damona import logger
logger.level = 10


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])



@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version=version)
def main():
    """This is the main help"""
    pass


@main.command()
@click.argument('name', type=click.STRING)
@click.option('--force', is_flag=True)
@click.option('--dryrun', is_flag=True, 
    help="If set, do not pull the image and do not create the binary alias")
@click.option('--from-url', help="""download image from a remote URL. The URL must
contain a registry.txt as explained on damona.readthedocs.io""") 
@click.option('--output-directory', default=images_directory, 
    help="""Where to save the image (default: {})""".format(images_directory))
def install(**kwargs):
    """Download and install an  image given its name and version (optional)

    Under Linux the DAMONA PATH is under ~/.config/damona

    """
    name = kwargs['name']
    from damona.pull import Pull
    p = Pull(dryrun=kwargs['dryrun'], from_url=kwargs['from_url'])
    p.pull(name, pull_folder=kwargs["output_directory"],
        force=kwargs['force'])


@main.command()
@click.argument('filename', required=True, type=click.STRING)
@click.option('--output-name', default=None, 
    help="default to the singularity extension and tag")
def build(**kwargs): #pragma: no cover
    """Build a container from a local recipes or damona recipes.

    You must have sudo permissions
    If FILENAME is not local, try to find it in Damona and build it.

        # a local recipes
        damona build ./Singularity.recipe

       # a recipe to be found in damona
        damona build salmon:1.3.0

    """
    cmd = "sudo singularity build {} {}"
    output_name = kwargs.get('output_name')
    if output_name is None:
        # get filename and save locally
        output_name = str(pathlib.Path(kwargs['filename']).name)
        output_name = output_name.replace("Singularity.", "")
        output_name = output_name.replace(":", "_") + ".img"
    else:
        assert output_name.endswith(('.sif', 'img'))

    if os.path.exists(kwargs['filename']) and os.path.isdir(kwargs['filename']) is False:
        cmd = cmd.format(output_name, kwargs['filename'])
    else:
        from damona import registry
        reg = registry.Registry()
        user_name = kwargs['filename']
        candidate = [x for x in reg._singularity_files 
            if x.endswith(user_name.replace(':', '_', 1))]
        if len(candidate) == 0:
            logger.critical(f'unknown image name {user_name}. use the command' +
                ' "damona list" to get correct names')
            sys.exit(1)
        logger.info("Building using damona recipes for {}".format(candidate[0]))
        cmd = cmd.format(output_name, candidate[0].replace(':', '_'))
    subprocess.call(cmd.split())


@main.command()
@click.option('--pattern', default=None, 
    help="restrict the output list keeping those with this pattern")
@click.option('--from-url', help="""download registry from remote URL. The URL must
contain a registry.txt as explained on damona.readthedocs.io. If you just type
'damona', the URL will be biomics.pasteur.fr/drylab/damona/registry.txt""") 
def list(**kwargs):
    """List all available images from Damona

    damona list
    damona list --from-url https://biomics.pasteur.fr/drylab/damona/registry.txt
    #This is the same command as above (alias)
    damona list --from-url damona

    """
    from damona.registry import Registry
    modules = Registry(from_url=kwargs["from_url"]).get_list(pattern=kwargs['pattern'])
    print(", ".join(modules))


@main.command()
@click.option('--create', type=click.STRING) 
@click.option('--delete', type=click.STRING) 
def env(**kwargs):
    """List the Damona environments"""
    from damona import Environ
    envs = Environ()
    if kwargs['create'] is None and kwargs['delete'] is None:
        print(f"There is currently only one base environment and {envs.N} user environment.")
        if envs.N !=0:
            print("Here are the current environment(s): ")
            for this in envs.environments:
                print(" -  {}".format(this))
        current_env = envs.get_current_env()
        logger.info("""Your current env is {}.

You can overwrite this behaviour by setting DAMONA_ENV variable.
For example under bash:

    export DAMONA_ENV="~/.config/damona/envs/your_best_env"


        """.format(current_env))
    elif kwargs['create'] and kwargs['delete']: # mutually exclusive
        logger.error("you cannot use --delete and --create together")
    elif kwargs['delete']:
        envs.delete(kwargs['delete'])
    elif kwargs['create']:
        envs.create(kwargs["create"])

@main.command()
@click.argument('name', required=True, type=click.STRING)
def activate(**kwargs):
    """activate a damona environment
    
    List the environments

        damona env

    and activate a valid one:

        damona activate example

    """
    from damona import Environ
    env = Environ()
    env.activate(kwargs['name'])

@main.command()
@click.option('--path', required=True, 
    help="path to recipes directory where Singularity file(s) can be found")
def registry(**kwargs):
    """Developers kit (eg build registry)"""
    from damona.registry import Registry

    if kwargs['path'] and os.path.exists(kwargs['path']):
        modules = Registry().create_registry(kwargs['path'])
    else:
        logger.critical('Please provide a valid path where to find Singulary from damona software')

if __name__ == "__main__": #pragma: no cover
    main()
