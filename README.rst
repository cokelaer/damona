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

Damona is now used in production to create reproducible environments where singularity images and their associated binaries are installed altogether.

In a nutshell, Damona combines the logic of Conda environments with the
reproducibility of singularity containers. We believe that it could be useful for
other projects and therefore decided to release it as an independent tool.

As of 30th Dec 2021, **Damona** contains 26 software, 38 releases, 105 binaries.

Installation
============

If you are in a hurry, just type::

    pip install damona --upgrade

You must install `Singularity <https://sylabs.io/docs>`_ to make use of **Damona**. 

If you are familiar with conda, I believe you can do::

    conda install singularity

Type **damona** in a shell. This will initiate the tool with a config file in your HOME/.config/damona directory for bash shell and `fish shell <https://fishshell.com/>`_ users.

Bash users should add this code in their ~/.bashrc file::

    source ~/.config/damona/damona.sh

and fishshell users should add the following code in their ~/.config/fish/config.fish file::

    source ~/.config/damona/damona.fish

Open a new shell and you are ready to go. Please see the `Installation in details`_ section for more information.

Quick Start
===========

**Damona** needs environments to work with.
First, let us *create* one, which is called TEST::

    damona env --create TEST

Second, we need to *activate* it. Subsequent insallation will happen in this environment::

    damona activate TEST

From there, we can install some binaries/images::

    damona install fastqc:0.11.9

That's it. Time to test. Type **fastqc**.

To rename this TEST example::

    damona env --rename TEST --new-name prod

or delete it::

    damona env --delete prod

See more examples hereafter or in the user guide on https://damona.readthedocs.io

Motivation
==========

As stated on their website, `Conda <https:/docs.conda.io/en/latest>`_ is
an open source **package** management system
and **environment** management system.
Conda provides pre-compiled releases of software; they can be installed in
different local environments that do not interfer with your system. This has
great advantages for developers. For example, you can install a pre-compiled
libraries in a minute instead of trying to compile it yourself including all
dependencies. Different communities have emerged using this
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

Although **Damona** was started with the `Sequana projet <https://sequana.readthedocs.io>`_,
**Damona** may be useful for others developers who wish to have a quick and easy
solution for their users when they need to install third-party libraries.

Before showing real-case examples, let us install the software itself and 
understand the details.



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
~/.config/damona directory. There, special files should be available:
**damona.sh**, **damona.fish**  and **damona.cfg**. Check that those files are present.

Finally, you need to tell your system where to find damona. For bashrc users,
please add this line to you bashrc file::

    source ~/.config/damona/damona.sh

open a new shell and type **damona** and you should be ready to go.

For fishshell users, please add this line in **~/.config/fish/config.fish***::

    source ~/.config/damona/damona.fish

Tutorial
============

The **Damona** standalone is called **damona**. It has a documentation that should suffice for most users.

The main documentation is obtained using::

    damona --help

where you will see the list of **Damona** commands (may be different with time) (may be::

    activate
    clean
    deactivate
    env
    export
    info
    install
    list
    remove
    search
    stats

To get help for the *install* command, type::

    damona install --help


1. *list* available environments
--------------------------------

By default you have an environment called **base**. Unlike the **base** environment found in **conda**, it is not
essential and may be altered. However, it cannot be removed or created. You can check the list of environments using::

    damona env

2. *create* environments
------------------------
All environments are stored in *~/.config/damona/envs/*. You can create a new one as follows::

    damona env --create TEST

There, you have a *bin* directory where binaries are going to be installed.

You can check that it has been created::

    damona env

Note the last line telling you that::

    Your current env is 'TEST'.

3. activate and deactivate environments
----------------------------------------

In order to install new binaries or software package, you must activate an environment. You may activate several but the last one is the *active* one. Let us activate the *TEST* environment::

    damona activate TEST

Check that it is active using::

    damona env

and look at the last line. It should look like::

    Your current env is 'TEST'.

What is going on when you activate an environment called TEST ? Simple: we append the directory ~/.config/damona/envs/TEST/bin to your PATH where binaries are searched for. This directory is removed when you use the *deactivate* command.

::

    damona deactivate TEST
    damona env 

should remove the TEST environment from your PATH. You may activate several and deactivate them. In such case, the
environments behave as a Last In First Out principle::

    damona activate base
    damona activate TEST
    damona deactivate 

Removes the last activated environments. While this set of commands is more specific::

    damona activate base
    damona activate TEST
    damona deactivate base

and keep the TEST environment only in your PATH.

4. **install** a software
--------------------------

Let us now consider that the TEST environment is active.

Damona provides software that may have several releases. Each software/release comes with binaries that will be
installed together with the underlying singularity image.::

    damona install fastqc:0.11.9

Here, the singularity image corresponding to the release 0.11.9 of the **fastqc** software is downloaded. Then, binaries registered in this release are installed (here the **fastqc** binary only).

All images are stored in *~/.config/damona/images* and are shared between environments. 


5. Get **info** about installed images and binaries
----------------------------------------------------

You can get the binaries installed in an environment (and the images used by
them) using the **info** command::

    damona info TEST


6. Search the registry
------------------------

By default, we provide recipes (26 in Dec 2021 ; 38 releases) available in **Damona**. 
They can be searched for using::

    damona search PATTERN

External registry can be set-up. For instance, a damona registry is accessible
as follows (for demonstration)::

    damona search fastqc --url damona

Where *damona* is an alias defined in the .config/damona/damona.cfg that
is set to https://biomics.pasteur.fr/drylab/damona/registry.txt

You may retrieve images from a website where a registry exists (see the developer
guide to create a registry yourself).


7. combine two different environments
--------------------------------------

In damona, you can have sereral environments in parallel and later activate the
one you wish to use. Let us create a new one::

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

========= ========================================================================
Version   Description
========= ========================================================================
0.8.3     * create registry specifically for the sandbox (for testing)
          * add damona community in the uploads
          * add pbbam, bioconvert, busco, canu, ccs
          * add polypolish, samtools 1.16.1, sequana 0.14.6, flye 2.9, canu 2.1.1
            circlator 1.5.5, hifiasm
0.8.2     * add idr, samtools, homer, bamtools, bedtools, sequana_denovo
          * add seqkit recipe and container
          * add shustring
0.8.1     * Include ability to interact with biocontainers by allowing retrieval
            of all biocontainers docker images using this syntax:
            'damona install biocontainers/xx:1.2.3' Note that although 9000 
            containers are available, in practice, only about 1000 dockers are 
            on dockerhub, which is already nice :-)
          * 
0.8.0     * Fix regression to install a software with its version
0.7.1     * Implement the fish shell 
          * add command "damona list"
          * rename recipes/ directory into software/ and created a new library/ 
            directory for images used as library, that are not installed.
0.7.0     * Check that singularity is installed
          * implement the remove command 
            https://github.com/cokelaer/damona/issues/15
          * more recipes cleanup (https://github.com/cokelaer/damona/issues/12)
          * removed damona recipes (pure python package)
          * cleanup all recipes
          * add zenodo stats (for admin)
0.6.0     * add ability to upload images on zenodo. No need for external 
            repositories.
          * ability to add/delete a software from different images
          * implement --help for the activate/deactivate (non trivial)
          * add --rename option in 'damona env'
          * 'base' environment is now at the same level as other environments
          * better bash script; no need for DAMONA_EXE variable anymore.
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
========= ========================================================================










