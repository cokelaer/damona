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

.. image:: https://static.pepy.tech/badge/damona
   :target: https://pepy.tech/project/damona


.. image:: https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C3.10-blue.svg
    :target: https://pypi.python.org/pypi/sequana
    :alt: Python 3.8 | 3.9 | 3.10 | 3.11 

.. image:: https://img.shields.io/github/issues/cokelaer/damona.svg
    :target: https://github.com/cokelaer/damona/issues
    :alt: GitHub Issues

:Python version: Python 3.8, 3.9, 3.10
:Source: See  `http://github.com/cokelaer/damona <https://github.com/cokelaer/damona/>`__.
:Issues: Please fill a report on `github <https://github.com/cokelaer/damona/issues>`__
:Platform: This is currently only available for Linux distribution with zsh/fish/bash shells (contributions are welcome to port the tool on other platforms/shells)

Overview
==========


.. image:: https://raw.githubusercontent.com/cokelaer/damona/refs/heads/main/doc/damona_logo.png
   :target: https://raw.githubusercontent.com/cokelaer/damona/refs/heads/main/doc/damona_logo.png
   :align: right
   :alt: logo
   :width: 300px


Damona is a singularity environment manager.

Damona started as a small collections of singularity recipes to help installing third-party tools for
`Sequana NGS pipelines <https://sequana.readthedocs.io>`_.  


Damona is now used in production to create reproducible environments where singularity images and their associated binaries are installed altogether.



In a nutshell, Damona combines the logic of Conda environments with the
reproducibility of singularity containers. We believe that it could be useful for
other projects and therefore decided to release it as an independent tool.

* As of Aug. 2024, **Damona** contains 87 containers (136 versions), which corresponds to 468 unique binaries.
* As of Oct. 2024, **Damona** contains 104 containers (155 versions), which corresponds to 514 unique binaries.

Installation
=============

Since **Damona** relies on **apptainer** (a.k.a. singularity), you must install `Apptainer <https://apptainer.org/docs/admin/main/installation.html>`_ to make use of **Damona**. This is the egg and chicken paradox. To get reproducible container with apptainer, at some point you need to install it. That the first
of the two software that you will need to install. Instructions
are on `singularity web site <https://sylabs.io/guides/3.6/user-guide/>`_. 

If you are familiar with conda, I believe you can do::

    conda install apptainer

I personally use the version available on my Fedora/Linux platform. Then install **Damona** using **pip** for Python::

    pip install damona

The first time, you use **Damona**, you need to type::

    damona

This will initiate the tool with a config file in your HOME/.config/damona directory.

Depending on your shell, you will be instructed to source a shell script. To make it persistent, you will need to update an environment file. For instance, under **bash** shell, add these lines in your .bashrc::

    if [ ! -f  "~/.config/damona/damona.sh" ] ; then
        source ~/.config/damona/damona.sh
    fi

Fish shell users should add the following code in their ~/.config/fish/config.fish file::

    source ~/.config/damona/damona.fish

Zsh users should add the following code in their ~/.config/fish/config.fish file::

    source ~/.config/damona/damona.zsh

Then, **open a new shell** and type **damona** again. You should see an help message:

.. image::  https://raw.githubusercontent.com/cokelaer/damona/refs/heads/main/doc/_static/cli.png

Quick Start
===========

**Damona** needs environments to work with. First, let us *create* one, which is called TEST::

    damona create TEST

Second, we need to *activate* it. Subsequent insallation will happen in this environment unless you open a new shell, or deactivate this environment::

    damona activate TEST

From there, we can install some binaries/images::

    damona install fastqc:0.11.9

That's it. Time to test. Type **fastqc**. This should open a graphical interface.

To rename this TEST environment, you may use::

    damona rename TEST --new-name prod

or delete it::

    damona delete prod

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




Tutorial
============

The **Damona** standalone is called **damona**. It has a documentation that should suffice for most users.

The main documentation is obtained using::

    damona --help

where you will see the list of **Damona** commands (may be different with time)::


    activate    Activate a damona environment.
    clean       Remove orphan images and binaries from all environments.
    create      Create a new environment
    deactivate  Deactivate the current Damona environment.
    delete      Remove an environment
    env         List all environemnts with some stats.
    export      Create a bundle of a given environment.
    info        Print information about a given environment.
    install     Download and install an image and its binaries.
    list        List all packages that can be installed
    remove      Remove binaries or image from an environment.
    rename      Rename an existing environment
    search      Search for a container or binary.
    stats       Get information about Damona images and binaries


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

    damona create TEST

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

You can search for a binary using::

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

    damone create test1

and check that you now have one more environment::

    damona env

We want to create an alias to the previously downloaded image of fastqc tool but
in the *test1* environment. First we activate the newly create environment::

    damona activate test1

then, we install the container::

    damona install fastqc:0.11.9

This will not download the image again. It will just create a binary in the
~/.config/damona/envs/test1/bin directory.

you can combine this new environment with the base one::

    damona activate base

If you are interested to know more, please see the User Guide and Developer
guide here below.


Contributors
============

Maintaining Sequana would not have been possible without users and contributors.
Each contribution has been an encouragement to pursue this project. Thanks to all:

.. image:: https://contrib.rocks/image?repo=cokelaer/damona
    :target: https://github.com/cokelaer/damona/graphs/contributors




Changelog
=========

From version 0.10 onwards, we will not mention the new software and their versions
but only changes made to the code itself.

========= ========================================================================
Version   Description
========= ========================================================================
0.14.2    * ADDED: AdapterRemoval, bbmap 39.01, dsrc 2.0.2, lima 2.9.0, 
            necat 0.0.1
0.14.1    * ADDED: ragtag 2.1.0, orthofinder 2.5.5, mcl , liftoff 1.6.3
          * Message if version is outdated
0.14      * ADDED: ir v2.8.0, vadr v1.6.4, seaview v5.0.5, repeatmasker 4.0.8
            bandage 0.8.1, rnammer 1.2, miniasm 0.3.0, hmmer 2.3.2 and 3.3.2
            infernal 1.1.5
          * NEW: progress bar for upload
          * CHANGES. fixed sandbox.zenodo upload
          * CHANGES: damona search with container sizes and recommendation
0.13      * Fix insallation of a registered software given a dockerhub link
          * Fix requests limits on zenodo (for the stats)
          * remove URLs section in config (will remove this feature)
          * handle docker:// link properly to pull image from registry
0.12.3    * ADDED dustmasker 1.0.0
          * update art with 2.1.8, 2.3.7, 2.5.8 versions
          * ADDED mosdepth 0.3.8
          * ADDED delly 1.2.6
          * UPDATED micromamba 1.5.8
0.12.2    * ADDED datasets
0.12.1    * ADDED pypolca, sratoolkit
0.12.0    * CORE development: rename zenodo-upload subcommand into upload
          * UPDATE rtools to v1.3.0 to include limma package
0.11.1    * ADD pbsim.
          * UPDATE hifiasm
0.11.0    * add precommit, update to use pyproject
0.10.1    * Fix the get_stats_software wrt new  zenodo API
0.10.0    * ADD zsh support
          * UPDATE flye 2.9.1
          * ADD nanopolish
          * UPDATE remove nanopolish from sequana_tools binaries
0.9.1     * ADD hmmer 3.2.2
          * ADD trinotate 4.0.1
          * ADD transdecode 5.7.0
          * ADD trinity 2.15.1
          * UPDATE bioconvert 1.1.0
          * update bowtie2 2.5.1
0.9.0     * refactorise the command 'env' by splitting into dedicated subcommands
            create, delete, rename. add progress bar when downloading container
          * NEW micromamba image to work as a localimage
          * NEW sequana_minimal package to hold common tools (bwa, samtools,
            kraken, etc)
          * NEW ivarm pangolin, nextclade, subread, mafft packages
          * UPDATE fastp to 0.23.3, gffread to 0.12.7 (3 times lighter).
          * UPDATE sequana_tools to use micromamba (30% lighter)
0.8.4     * fix damona stats command to return unique binaries
          * more recipes and version (e.g. fastqc 0.12.1, graphviz update, etc)
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
