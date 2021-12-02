Developer guide
===============

Developers are lucky: they can do more than users. If you type::

    damona --help

you will have the users' commands. However, they are more commands available. 
They are not shown because they are attended to be used by developers only.

The first useful commands for developers is the **build** command::

    damona build --help

The second is the **zenodo-upload** command::

    damona zenodo-upload --help



All images will be posted on Zenodo
------------------------------------

The goal is to have a unique and official DOI for each tool.

    git clone git@github.com/your_fork/damona
    cd damona

Let us consider an example calle SOFTWARE. You must be in the directory:

    cd recipes/SOFTWARE

Case 1: the tool does not exists.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create a new Singulariry image. Time to upload the resulting (functional !) image::

    damona zenodo-upload SOFTWARE_1.0.0.img --mode zenodo

It creates a registry.yaml file with the metadata ready to commit and push


Case 2: the recipe exists already
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`

Create a new Singulariry image. Time to upload the resulting (functional !) image::

    damona zenodo-upload SOFTWARE_2.0.0.img --mode zenodo


It updates the existing registry.yaml ready to commit and push



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


You may have underscore in your package name
build
-----

To test the recipes, type::

    damona build pkgname:x.y.z

This is just an alias to singularity build command::

    sudo singularity build pkgname.img Singularity.pkgname_x.y.z


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
executables) will install all the binaries that are provide in the registry. 

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

md5sum is optional and used if present to not re-download a file, if it is
already present, so it is quite useful to provide.


Where are stored the containers ?
----------------------------------

Originally, we stored the container in this collections  https://cloud.sylabs.io/library/cokelaer/damona but we extended **Damona** so that it can fetch containers from other places. The principle is quite simple; you put containers on a web site, place registry.txt file in there, which is just a concatenation of registry for all software that are available.

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


