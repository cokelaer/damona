DAMONA
######

.. image:: https://badge.fury.io/py/damona.svg
    :target: https://pypi.python.org/pypi/damona


.. image:: https://github.com/cokelaer/damona/actions/workflows/main.yml/badge.svg
   :target: https://github.com/cokelaer/damona/actions/workflows/main.yml

.. image:: https://coveralls.io/repos/github/cokelaer/damona/badge.svg?branch=master
    :target: https://coveralls.io/github/cokelaer/damona?branch=master

.. image:: http://readthedocs.org/projects/damona/badge/?version=latest
    :target: http://damona.readthedocs.org/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: https://zenodo.org/badge/282275608.svg
   :target: https://zenodo.org/badge/latestdoi/282275608


:Python version: Python 3.7, 3.8, 3.9
:Source: See  `http://github.com/cokelaer/damona <https://github.com/cokelaer/damona/>`__.
:Issues: Please fill a report on `github <https://github.com/cokelaer/damona/issues>`__
:Platform: This is currently only available for Linux distribution with bash shell (contributions are welcome to port the tool on MacOSX and other platforms)

Overview
========

Damona is a singularity environment manager.

Damona started as a small collections of singularity recipes to help installing third-party tools for
`Sequana NGS pipelines <https://sequana.readthedocs.io>`_.

Damona is now used to create environments where singularity images and their associated binaries can be installed altogether.

In a nutshell, Damona combines the logic of Conda environments with the
reproducibility of singularity containers. We believe that it could be useful for
other projects and therefore decided to release it as an independent tool.

Installation
============

If you are in a hurry, just type::

    pip install damona --upgrade

and install `Singularity <https://sylabs.io/docs>`_. 

Type **damona** in a shell. This will initiate the tool with a config file in your HOME/.config/damona directory.
Open a new shell and you are ready to go. Please the `Installation in details`_ section for more information.

Motivation
==========

As stated on their website, `Conda <https:/docs.conda.io/en/latest>`_ is
an open source **package** management system
and **environment** management system.
Conda provides pre-compiled releases of software; they can be installed in
different local environments that do not interfer with your system. This has
great advantages for developers. For example, you can install a pre-compiled
libraries in a minute instead of trying to compile it yourself including all
dependencies. Different communities have emerge using this
framework. One of them is `Bioconda <https://bioconda.github.io>`_, which is dedicated to bioinformatics.

Another great tool that emerged in the last years is
`Singularity <https://sylabs.io/docs>`_. Singularity containers can be used
to package entire scientific workflows,
software and libraries, and even data. It is a simple file that can be shared
between environments and guarantee exectution and reproducibility.

Originally, Conda provided pre-compiled version of a software. Nowadays, it also provides
a docker and a singularity image of the tool. On the other side, Singularity can include an
entire conda environment. As you can see everything is there to build reproducible tools and
environment.

Now, what about a software in development that depends on third-party packages ? 
You would create a conda environment and starts installing the required packages.
Quickly, you will install another package that will break your environment due
to unresolved conlicts; this is not common but it happens. In the worst case
scenario, the environment is broken. In facilities where users depends on you,
it can be quite stresful and time-consuming to maintain several such
environments. This is why we have moved little by little to a very light conda
environment where known-to-cause-problem packages have been shipped into
singularity containers. This means we have to create aliases to those
singularities. The singularities can be simple executable containers or full
environment containers with many executables inside. In both cases, one need to
manage those containers for different users, pipelines, versions etc. This
started to be cumbersome to have containers in different places and update
script that generate the aliases to those executables.


That's where **damona** started: we wanted to combine the conda-like environment 
framework to manage our singularity containers more easily.

Although it was start with the Sequana projet, 
**Damona** may be useful for others developers who wish to have a quick and easy
solution for their users when they need to install third-party libraries.

Before showing real-case examples, let us install the software itself.



Installation in details
=======================

The is the egg and chicken paradox. To get reproducible container with
singularity, at some point you need to install singularity itself. That the first
of the two software that you will need to install. Instructions
are on `singularity web site <https://sylabs.io/guides/3.6/user-guide/>`_. This
is not obvious to be honest. You need the GO language to be installed as well. I
personally installed from source and it worked like a charm.

Second, you need **Damona**. This is a pure Python sotfware with only a few
dependencies. Install it with the **pip** software provided with your Python
installation (Python 3.X)::

    pip install damona --upgrade

Type **damona** to create the Damona tree structure. Images and binaries 
will be saved in your home directory within the
~/.config/damona directory. There, two special files should be available:
**damona.sh** and **damona.cfg**. Check that those files are present.

Finally, you need to tell your system where to find damona. For bashrc users,
please add those two lines to you bashrc file::

    source ~/.config/damona/damona.sh

open a new shell and type **damona** and you should be ready to go.

Quick Start
============

1. *list* available environments
--------------------------------

By default you have an environment called **base**. You can check the list of
environment and their contents at any time using::

    damona env

2. list installed images and binaries
-------------------------------------

You can get the binaries installed in an environment (and the images used by
them)::

    damona info base

3. Search the registry
------------------------

By default, we provide some recipes (for testing mostly but also to complement existing
registries when a tool is missing) and their images. They can be searched for using::

    damona search PATTERN

External registry can be set-up. For instance, the damona registry is accessible
as follows::

    damona search fastqc --url damona

Where *damona* is an alias defined in the .config/damona/damona.cfg that
actullay looks for https://biomics.pasteur.fr/drylab/damona/registry.txt

You may retrieve images from a website where a registry exists (see the developer
guide to create a registry yourself).

4. Activate an environment
--------------------------

::

    damona activate base

4. *install* a Damona image
----------------------------

Download and install an image in your activate environment::

    damona install fastqc:0.11.9

This will download the container in your ./config/damona/images directory and create an
executable for you in ~/.config/damona/bin.

This is your *base* environment. All images are stored in this directory
*~/.config/damona/images*. By default binaries are stored in the *~./config/damona/envs/base/bin* directory.

To benefit from thoses binaries, you must change your PATH accordingly using::

    export PATH=~/config/damona/bin:$PATH



5. **activate/deactivate** command
----------------------------------

You can change your PATH environment on the fly to use one or several
environments. However, we provide a more convenient mechanism based on **conda** commands. If you want to used your based environment, you can simply activate it using::

    damona activate base

Once done, you can quit the shell or deactivate your environment specically
using its name ::

    damona deactivate base

or if you just wish to deactivate the last environment that you have activated::

    damona deactivate

You can call this commands several times until no more **damona** environments
are active.

3. combine two different environments
--------------------------------------

In damona, you can have sereral environments in parallel and later activate the
ones you wish to use. Let us create a new one::

    damone env --create test1

and check that you now have one more environment::

    damona env

We want to create an alias to the previously downloaded image of fastqc tool but
in the *test1* environment. First we activate the newly create environment::

    damona activate test1

then, we install the container::

    damona install fastqc:0.11.9

This will not download the image again. It will just create a binary in the
~/.config/damona/envs/test1/bin directory.

you can combine this new environemnt with the base one::

    damona activate base

If you are interested to know more, please see the User Guide and Developer
guide here below.

Changelog
=========

========= ====================================================================
Version   Description
========= ====================================================================
0.6.0     * add ability to upload images on zenodo. No need for external 
            repositories.
          * ability to add/delete a software from different images
          * implement --help for the activate/deactivate (non trivial)
          * add --rename option in 'damona env'
          * 'base' environment is now at the same level as other environments
0.5.3     * Fixing config/shell 
0.5.2     * add missing shell package
0.5.1     * add DAMONA_SINGULARITY_OPTIONS env variable in the binary
          * Fix the way binaries are found in the releases.
          * new recipes: rtools
          * new releases: sequana_tools_0.10.0
          * Fix shell script to handle DAMONA_EXE variable 
0.5.0     * Major refactoring. 

            - Simplification of the registries (dropping notion of exe/set 
              class
            - Main script should now be fully functional with functional
              activation/deactivation. 
            - New command to build images from local recipes or dockerhub 
              entries.
            - Install command can now install local container. 
            - DAMONA_PATH can be set to install damona images/binaries 
              anywhere, not just in local home. 
            - check md5 of images to not download/copy again
0.4.3     * Implement damona activate/deactivate
0.4.2     * Fix typo in the creation of aliases for 'set' containers
0.4.1     * implemented aliases for the --from-url option stored in a
            damona.cfg file
0.4.0     * implemented the 'env' and 'activate' command
          * ability to setup an external registry on any https and retrieve
            registry from there to download external images
0.3.X     * add gffread, rnadiff recipes
0.3.0     * A stable version with documentation and >95% coverage read-yto-use
0.2.3     * add new recipes (rnadiff)
0.2.2     * Download latest if no version provided
          * include *build* command to build image locally
0.2.1     fixed manifest
0.2.0     first working version of damona to pull image locally with binaries
0.1.1     small update to fix RTD, travis, coveralls
0.1       first release to test feasibility of the project
========= ====================================================================










