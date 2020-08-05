DAMONA
######

Damona is a collections of singularity recipes that can be used to build software used in
NGS pipelines. Damona allows a quick and easy installation of the related
containers. If you prefer, you can build the container images locally as well.

.. image:: https://badge.fury.io/py/damona.svg
    :target: https://pypi.python.org/pypi/damona

.. image:: https://travis-ci.org/cokelaer/damona.svg?branch=master
    :target: https://travis-ci.org/cokelaer/damona

.. image:: https://coveralls.io/repos/github/cokelaer/damona/badge.svg?branch=master
    :target: https://coveralls.io/github/cokelaer/damona?branch=master 

.. image:: http://readthedocs.org/projects/damona/badge/?version=latest
    :target: http://damona.readthedocs.org/en/latest/?badge=latest
    :alt: Documentation Status


:Python version: Python 3.6, 3.7.3
:Source: See  `http://github.com/cokelaer/damona <https://github.com/cokelaer/damona/>`__.
:Issues: Please fill a report on `github <https://github.com/cokelaer/damona/issues>`__

Motivation
==========

Why another collections or tools to provide NGS images ? There is `Bioconda
<https://bioconda.github.io/>`__, and
a bunch of collections of singularity images indeed !

Yet, Bioconda may have limitations for end-users. One of them is that two tools may be impossible to cohabit or slow to install due to difficulties in resolving their dependencies. Second, singularity images posted here are there are a great source of inspirations. Yet, I wanted a very simple tool both for developers that wish to offer an easy installation and for users to whom we try to hide all the nitty-gritty details of installing third-party librairies.

Our goal is not to replace existing initiative but just to complement them when
required. In particular, we designed **damona** so as to provide the executables
required by `Sequana <sequana.readthedocs.io>`_ pipelines.

We will therefore maintain damona in the context of Sequana project. Yet,
**Damona** may be useful for others developers who wish to have a quick and easy
solution for their users when they need to install third-party libraries

Installation
============

1. Install singularity: https://sylabs.io/guides/3.0/user-guide/installation.html
2. Install **Damona** using **pip**. You will need Python 3.X::

    pip install damona --upgrade

The dependencies of **Damona** are pure python so it should be straightfoward.

Usage
=====


Print the list of images available within Damona collections::

    damona list

Download the one you want to use::

    damona pull fastqc:0.11.9

This will download the container in your ./config/damona directory and create an
executable for you in ~/.config/damona/bin. 

You just need to append your PATH. For instance under Linux, type:

    export PATH=~/config/damona/bin:$PATH

You you can also add in your .profile or .bashrc file for this command to be
permanent.

You are ready to go. Just type this command to use the newly installed container::

    fastqc --help

Check that you have not installed another version::

    which fastqc

This should show you the path *~/.config/damona/bin/fastqc*. Of course, tThis tool is pretty common in NGS and can be easily installed. This is more a toy example than a real example.

In damona there are three classes of container:

1. executables (like the one above)
2. environement: for instance, we provide an image for R v4.0.2. This is not a NGS tool per se but can be used to build other containers. 
3. Set of executables (coming soon)



Changelog
=========

========= ====================================================================
Version   Description
========= ====================================================================
0.2.3     * add new recipes (rnadiff) 
0.2.2     * Download latest if no version provided
          * include *build* command to build image locally
0.2.1     fixed manifest
0.2.0     first working version of damona to pull image locally with binaries
0.1.1     small update to fix RTD, travis, coveralls
0.1       first release to test feasibility of the project
========= ====================================================================










