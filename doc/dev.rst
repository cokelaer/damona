Developer guide
===============

tree structure
--------------

Recipes are in the ./recipes directory with one sub-directory per tool or environment.
Inside a sub directory (e.g, R, conda) you may have several recipes for
different version

For example, for **damona** there is a directory called **damona**. Inside that
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

Currently containers are hosted in this collection: https://cloud.sylabs.io/library/cokelaer/damona
