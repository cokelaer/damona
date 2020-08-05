User Guide
##########

Print the list of available containers
---------------------------------------

**damona** contains just a few containers. As explained in the motivation, other
community provide thousands of container but here we provide container used in
Sequana projects. 

To get a list of the available containers, just type::

   damona list 

You should see the container names and their version::

   conda:4.7.12, damona:0.3.0, fastqc:0.11.9, kraken:1.1, kraken:2.0.9, prokka:1.14.5, r:3.6.3, r:4.0.2, rnadiff:1.7.0, salmon:1.3.0

You can filter by selecting a specific pattern::

    damona list --pattern qc

Download and install an image
-----------------------------

You can download a conainer image as follows::

    damona install fastqc:0.11.9

If there are several version and you just want the latest, remove the tag::

    damona install fastqc

That's it, you should get the image in your config path ~/.config/damona/images
directory. In addition, a binary alias is created in ~/.config/damona/bin

The container is a Singularity container. **Damona** is just a simple wrapper
around Singularity. For example::

    singularity run name.img fastqc

Should run the container and launch the executable *fastqc* to be found inside.
With Damona, we provide a simple framework that ease the life of the developer
and user. We have indeed a simple registry system stored with each recipe. When
required, we create a binary in ~/.config/damona/bin/fastqc named after the recipe name.

All you need to do is call the executable from this directory. Even better, set
your environment to look for executables in ~/.config/damona/bin/ For example::

    export PATH=~/.config/damona/bin/:$PATH

and you are ready do go.

The *develop* command
---------------------

This is for developers. When a new recipe is added, we must provide a registry.
The skelton of that registry can be printed as follows::

    damona develop ./recipes/name_of_directory

This command searches for Singularity files and prints what the registry should
look like. See the developer guide for more details

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

Setup the environement
----------------------

Binaries are saved into ~/.config/damona/bin

To make those binaries available, change your path. For example under bash::

    export PATH=~/.config/damona/bin:$PATH

To make it persisent add the previous line into your .bashrc file.
