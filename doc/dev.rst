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

The second is the **zenodo-upload** command::

    damona zenodo-upload --help


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

    damona zenodo-upload SOFTWARE_1.0.0.img --mode zenodo

This command uploads the image on Zenodo with all correct metadata already pre-filled for you. It also
creates a registry.yaml file with the metadata ready to commit and push. **edit the registry file to add a binaries section if neeeded**.


Case 2: the recipe exists already
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create a new Singularity image. Time to upload the resulting (functional !) image::

    damona zenodo-upload SOFTWARE_2.0.0.img --mode zenodo

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

There is no specific instructions. The simpler the better. Please try to reuse 
existing dockers, singularity. For example, we have a conda recipes. Try to make the final container
as small as possible.


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
2. an image on the damona website. For instance with ucsc recipes, we stored it on the damona URL, which is::

       download: damona::ucsc_0.1.0.img

   it will look for the damona URL. This is an alias to https://biomics.pasteur.fr/salsa/damona/ucsc_0.1.0.img
3. an image stored on syslab.io::

   library://cokelaer/damona/conda:4.7.12




Where are stored the containers ?
----------------------------------

Since Dev 2021, we store containers with a DOI on Zenodo website. Originally, we stored some container here: https://cloud.sylabs.io/library/cokelaer/damona but we extended **Damona** so that it can fetch containers from other places. If you have your own containers, it is quite simple to create a registry and place it anywhere on the web and inform damona that you want to use that registry.

We have an example on https://biomics.pasteur.fr/salsa/damona



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


Upload image on sylabs
----------------------

::

    singularity build salmon.img Singularity.salmon_1.3.0
    singularity sign salmon.img
	singularity push salmon.img library://cokelaer/damona/salmon:1.3.0

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







