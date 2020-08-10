DAMONA
######

Damona is a singularity environment manager.

Damona started as a small collections of singularity recipes to help installing third-party tools for 
`Sequana pipelines <a href="https://sequana.readthedocs.io>`_ and is now used to 
download singularity images but more importantly set different environments (e.g. one per pipeline).

In a nutshell, it puts together the logic of Conda environments with the
reproducibility of singularity containers. We believe it could be useful for
other projects and therefore decided to release it.

.. image:: https://badge.fury.io/py/damona.svg
    :target: https://pypi.python.org/pypi/damona

.. image:: https://travis-ci.org/cokelaer/damona.svg?branch=master
    :target: https://travis-ci.org/cokelaer/damona

.. image:: https://coveralls.io/repos/github/cokelaer/damona/badge.svg?branch=master
    :target: https://coveralls.io/github/cokelaer/damona?branch=master 

.. image:: http://readthedocs.org/projects/damona/badge/?version=latest
    :target: http://damona.readthedocs.org/en/latest/?badge=latest
    :alt: Documentation Status


:Python version: Python 3.6, 3.7.3, 3.7, 3.8
:Source: See  `http://github.com/cokelaer/damona <https://github.com/cokelaer/damona/>`__.
:Issues: Please fill a report on `github <https://github.com/cokelaer/damona/issues>`__

Motivation
==========

As stated on their website, `Conda <https:/docs.conda.io/en/latest>`_ is 
an open source **package** management system 
and **environment** management system.
Conda provides pre-compiled releases of software; they can be installed in
different local environment that do not interfer with your system. This has
great advantages for developers. Different community have emerge using this
framework. One of them is `Bioconda <https://bioconda.github.io>`_, which is dedicated to bioinformatics.
Although great, it is sometimes tricky to re-install an environment simply
because NGS pipelines relies on many different software and different versions
may be in conflicts. Another great tool is
`Singularity <https://sylabs.io/docs>`_. Singularity containers can be used 
to package entire scientific workflows, 
software and libraries, and even data. It is a simpe file that can be shared
between environments and guarantee exectution and reproducibility. 

Originally, Conda provided pre-compiled version of a package. Nowadays, it also provides
a docker and a singularity image of the tool. Singularity can package an 
entire conda environment. 
As you can see everything is there to build reproducible tools and
environment. 

Now, what about a software in development that depends on third-party packages
You would create a conda environment and starts installing those packages.
Quickly, you will install another package that will break your environment due
to unresolved conlicts; this is not common but it happens. In the worst case
scenario, the environment is broken. In facilities where users depends on you,
it can be quite stresful and time-consuming to maintain several such
environments. This is why we have moved little by little to a very light conda
environment where known-to-cause-problem packages have been shipped into
singularity containers. This means we have to create aliases to those
singularities. The singularities can be simple executable containers or full
environment containers with many executables inside. In both cases, on need to
manager those containers for different users, pipelines, versions etc. This
started to be cumbersome to have containers in different places and update
script that generate the aliases to those executables. 


That's where **damona** started: we wanted to combine the conda-like environment framework to manage our singularitiy containers.  

Our goal is not to replace existing registry of biocontainers such as
biocontainers but to use existing images, download them and manage them locally.
Although **Damona** has some recipes and images (on
sylabs/cokelaer/damona dn https://biomics.pasteur.fr/drylab/damona), those
containers are for testing and help managing and installing the third-party
tools required by `Sequana <sequana.readthedocs.io>`_ pipelines.

We will therefore maintain damona in the context of Sequana project. Yet,
**Damona** may be useful for others developers who wish to have a quick and easy
solution for their users when they need to install third-party libraries

Installation
============

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

You should be ready to go. 

Quick Start
============

1. *list* available containers
-------------------------------
By default, we provide some recipes (for testing mostly but also to complement existing
registries when a tool is missing) and their images. 

To get the list images available within **Damona** collection, just type::

    damona list --from-url https://biomics.pasteur.fr/drylab/damona/registry.txt

or in short (just for that url)::

    damona list --from-url damona

You may retrieve images from a website where a registry exists (see developer
guide to create a registry)

2. *install* an image
---------------------

Download the one you want to use::

    damona install fastqc:0.11.9

This will download the container in your ./config/damona directory and create an
executable for you in ~/.config/damona/bin. 

This is your *base* environment. By default there is only one and all images
will be stored in this directory. 

The binaries are in the ~./config/damona/bin directory and you may need to append this path to 
your PATH environmental variable. For instance under Linux, type::

    export PATH=~/config/damona/bin:$PATH

That's it. You have downloaded a reproducible container and you can try::

    fastqc --versio

Check that this is the correct path::

    which fastqc

3. combine two different environments
--------------------------------------

If you type::

    damona env

it will list the environments you currently hosting. Since you are starting,
most probably you have only the base environment. Let us create a new one::

    damone env --create test1

and check that you now have 1 environment::

    damona env

We want to create an alias to the previously downloaded image of fastqc tool but
in the *test1* environment. First we activate it by setting an environmental
variable::

    export DAMONA_ENV=~/.config/damona/envs/test1
    export DAMONA_PATH=~/.config/damona/envs/test1/bin

.. note:: the command::

        damona env activate

    does not currently change the environmental variables (cannot be done 
    permanently in Python) but we gives hints on how to do it.

then, we install the container::

    damona install fastqc:0.11.9

This will not download the image again. Instead it will create an alias in
~/.config/damona/envs/test1/bin directory

Change your PATH accordingly using the DAMONA_PATH variable

If you are interested to know more, please see the User Guide and Developer
guide here below.

Roadmap
=======

**Damona** is pretty new but here is short roadmap

* check the md5 of the downloaded file so as to avoid overwritten existing name
* do we store all images in the damona/images or do we store them in individual
  environement (with possbile duplicates).
* remove the build and develop command most probably. The develop that builds a
  registry could be reaplce by a simple python code that builds the registry on
  the fly. the registry.yaml may not be required after all. Could be a simple
  registry.txt file name and version are included in the name. 
* ability to download any image from internet if user provide the name and
  version to cope with different naming conventions; 
* remove registry from recipes if possible and put metadata inside the
  singularity. If not found, a registry is required

Changelog
=========

========= ====================================================================
Version   Description
========= ====================================================================
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










