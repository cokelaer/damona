Developer guide
===============

tree structure
--------------

Recipes are in ./recipes where each sub directory is related to one container. 
Inside a sub directory (e.g, R, conda) you may have several recipes. 

For example, for **damona** there is a directory called **damona**. Inside that
directory, if there is only one recipes, name it::

   Singularity.damona

If you wish to have several recipes for different version, name it::

   Singularity.damona_x.y.z

You may simplify it as::

   Singularity.damona_x.y

if the micro version is 0 and ::

   Singularity.damona_x

if the minor and micro version are 0 or unknown.

Naming convention
-----------------

Singularity recipes must be named as Singularity.PKGNAME_x.y.z

Note that PKGNAME could be in small or big caps but the final image with be all
lower caps (singularity-hub feature). Consequently, when downloading an image,
it should be named as pkgname_x.y.z

build
-----

Add a Makefile wihh an entry for each Singularity. This will be useful for local
build.

Singularity recipes
--------------------

IF the class of image is executable, please add these lines::

    %runscript
        exec THE_EXE_NAME "$@"

so one can run it simply as ::

    singularity run image.img 


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

    {
        "Singularity_kraken_1.1": {
            type": "executable"
            "executables": {
                "kraken": "kraken"
            }
        },
        "Singularity_kraken_2": {
            type": "executable"
            "executables": {
                "kraken2": "kraken2"
            }
        }
    }

