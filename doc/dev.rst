Developer guide
===============

tree structure
--------------

Recipes are in the ./recipes directory with one sub-directory per tool or environment.
Inside a sub directory (e.g, R, conda) you may have several recipes for
different versions

For example, for **Damona** there is a directory called **Damona**. Inside that
directory, if there is only one recipes, name it::

   Singularity.damona

If you wish to have several recipes for different version, name it::

   Singularity.damona_x.y.z

Naming convention
-----------------

Singularity recipes must be named as Singularity.PKGNAME_x.y.z

Note that PKGNAME could be in small or big caps but the final image with be all
lower caps (singularity-hub feature). Consequently, when downloading an image,
it should be named as pkgname_x.y.z

build
-----

To test the recipes, type::

    damona build pkgname:x.y.z 

Singularity recipes
--------------------

We have three types of recipes:

1. executable
2. environment
3. sets of executables

If the class of image is executable, please add these lines::

    %runscript
        exec THE_EXE_NAME "$@"

so one can run it simply as ::

    singularity run image.img 

The class *environement* is suppose to be used to build other container. When
installing a *executable* container, a binary is created in ~/.config/damona/bin
but no such files are created for *environement*. The final class (set of
executables) is not yet implemented. 

registry
---------

For each singularity, a registry is required. It containts a json with the type
of each singularity: does it provide a single tool or an environment or a set of
executables.

The different container types can be:

* executable: a container aiming at providing a single executable
* class_type: A container to be used to build an 'executable' or 'environment'
* environment: A a container with a set of executables

::

    Singularity.kraken_1.1:
        version: 1.1
        download: library://cokelaer/damona/kraken:1.1
        class: "exe"
        binaries:
            - kraken: "kraken"
    Singularity.kraken_2.0.9:
        version: 2.0.9
        download: library://cokelaer/damona/kraken:2.0.9
        class: "exe"
        binaries:
            - kraken2: "kraken2"

Where are stored the containers ?
----------------------------------

Originally, we stored the container in this collections  https://cloud.sylabs.io/library/cokelaer/damona but we extended **Damona** so that it can fetch containers from other places. The principle is quite simple; you put containers on a web site, place registry.txt file that lists the images as follows::

    [exe]
    name1_x.y.z.img
    name2_x.y.z.img
    [env]
    name3_x.y.z.img
    [set]
    name4_x.y.z.img

The image found from the [exe] section will have an alias created. The name of
the alias with be the prefix (before the first _ character).

We have such as example on https://biomics.pasteur.fr/drylab/damona



The *registry* command
------------------------

This is for developers. When a new recipe is added, we must provide a registry.
The skeleton of that registry can be printed as follows::

    damona registry ./recipes/name_of_directory

This command searches for Singularity files and prints what the registry should
look like. See the registr guide for more details

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

