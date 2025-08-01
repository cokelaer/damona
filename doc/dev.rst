Developer guide
===============


.. contents:: Table of Contents

Introduction
------------


Developers are lucky: they can do more than users. If you type::

    damona --help

you will have the users' commands. However, they are more commands available.
They are not shown because they are intended for developers only.

The first useful command for developers is the **build** command::

    damona build --help

The second is the **upload** command::

    damona upload --help


All images will be posted on Zenodo if Singularity recipe is in Damona
----------------------------------------------------------------------

The goal is to have a unique and official DOI for each tool.
::

    git clone git@github.com/your_fork/damona
    cd damona

Let us consider an example called SOFTWARE. You must be in the directory of the SOFTWARE package::

    cd recipes/SOFTWARE

.. warning:: the following required registered token on Zenodo and will upload
    images on Zenodo as well ! Consider removing the --mode zenodo to try
    the sandbox version

Case 1: the tool does not exist.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create a new Singularity image. Time to upload the resulting (functional !) image::

    damona upload SOFTWARE_1.0.0.img --mode zenodo

This command uploads the image on Zenodo with all correct metadata already pre-filled for you. It also
creates a registry.yaml file with the metadata ready to commit and push. **edit the registry file to add a binaries section if neeeded**.


Case 2: the recipe exists already
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create a new Singularity image. Time to upload the resulting (functional !) image::

    damona upload SOFTWARE_2.0.0.img --mode zenodo

It updates the existing registry.yaml ready to commit and push

tree structure
--------------

Recipes are in the ./recipes directory with one sub-directory per tool or environment.
Inside a sub directory (e.g, R, conda) you may have several recipes for
different versions.

For example, for **Damona** there is a directory called **Damona**. Inside that
directory, if there is only one recipes, name it::

   Singularity.damona

If you wish to have several recipes for different version, name it::

   Singularity.damona_x.y.z

Naming convention
-----------------

A valid singularity image must have the following name::

        Singularity.NAME_x.y.z
        Singularity.NAME_SUFFIX_x.y.z

Underscore can be part of the name.

Images names for users will appear as::

     NAME:x.y.z
     NAME_SUFFIX:x.y.z


Note that NAME could be in small or big caps but the final image with be all
lower caps (singularity-hub feature). Consequently, when downloading an image,
it should be named as pkgname:x.y.z


building
--------

To test the recipe, type::

    damona build pkgname:x.y.z

This is just an alias to singularity build command::

    sudo singularity build pkgname.img Singularity.pkgname_x.y.z


Singularity recipes
--------------------

Here are some instructions to help writting recipes.


Try to set version instead of latest::


    BootStrap: docker
    From: mambaorg/micromamba:1.4.4

is better than ::

    BootStrap: docker
    From: mambaorg/micromamba:latest


By experience here are some conventions that could be useful. These commands are useful to avoid warnings when running the container ::

    %environment
        LANG=C.UTF-8
        LC_ALL=C.UTF-8
        export LANG LC_ALL



No need for labels but if you want, you may add a labels section::

    %labels
        whatever

No need for help section.


A useful set of commands is also to add test within the container but this is only tested when building the recipes:

    %test
      command --help

Singularity recipes from micromamba
------------------------------------

A classic recipes is the one based on micromamba. We build a micromamba image in ./library/micromamba and can be reused as follow to install any tool from conda::


    Bootstrap: localimage
    From: micromamba_1.5.8.img

    %post
        apt -y update && apt -y upgrade

        # export the PATH here so that pip is found later on
        export PATH=$PATH:/opt/conda/envs/main/bin/
        # an alias
        export OPTS=" -q -c conda-forge -c bioconda -n main -y "

        micromamba install $OPTS python="3.9"
        micromamba install $OPTS "art==3.19.15"

        # cleanup
        micromamba clean --packages -y
        micromamba clean --all -y
        rm -rf /opt/condas/pkg

    %environment
        export PATH=$PATH:/opt/conda/envs/main/bin/

    %runscript
        art_illumina "$@"



registry
---------

For each singularity, a registry is required. It contains a yaml file that looks
like

::

    fastqc:
        0.11.9:
            download: URL1
            md5sum:
            binaries: fastqc
        0.11.8:
            download: URL
            md5sum:
            binaries: fastqc

::

    fastqc:
        binaries: fastqc
        0.11.9:
            download: URL1
            md5sum:
        0.11.8:
            download: URL
            md5sum:


The download link can be of three types:

1. a valid URL
2. an image stored on docker e.g. "docker://biocontainers/hisat2:v2.1.0-2-deb_cv1"





Where are stored the containers ?
----------------------------------

Since Dev 2021, we store containers with a DOI on Zenodo website. Originally, we stored some container here: https://cloud.sylabs.io/library/cokelaer/damona but we extended **Damona** so that it can fetch containers from other places. If you have your own containers, it is quite simple to create a registry and place it anywhere on the web and inform damona that you want to use that registry. **damona** works with its own online registry on github.

If you do not want to use the online registry (always up-to-date), or do not have internet connection, you can use::

    damona search fastqc --local-registry-only
    damona install fastqc --local-registry-only



Build an image locally
----------------------

Sometimes, the version you are looking for is not available. It is quite easy to
rebuild the recipes yourself and store it locally.::

    damona build Singularity.recipes

Again, this is just a wrapper around singularity build command. The advantage
here is that we can use this command to buld a damona recipes::

    damona build fastqc:0.11.9

You can then save the image elsewhere if you want::

    damona build fastqc:0.11.9  --output-name ~/temp.img

This is nothing more than an alias to singularity itself::

     singularity build recipes Singularity.recipes

More interesting is the ability to build a local version of a recipes to be
found in damona::

    damona build salmon:1.3.0

this will find the recipes automatically and save the final container in
**salmon_1.3.0.img**.


What about reusing a docker image
----------------------------------


You can. See for example the hisat2 image here: https://github.com/cokelaer/damona/tree/master/damona/recipes/hisat2

It looks like::


    hisat2:
        releases:
          2.1.0:
            download: docker://biocontainers/hisat2:v2.1.0-2-deb_cv1
            binaries: hisat2 hisat2-build
            md5sum: e680e5ab181e73a8b367693a7bd71098

Here, there is no zenodo link though because it is already on docker.
