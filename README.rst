DAMONA
######

Damona is a collections of singularity recipes that can be used to build software used in
NGS pipelines. It provides a simple excutable to download and configure the
images locally. 

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
:Source: See  `http://github.com/damona/damona <https://github.com/damona/damona/>`__.
:Issues: Please fill a report on `github <https://github.com/damona/damona/issues>`__

Motivation
==========

Why another collections or tools to provide NGS images ? There is bioconda, and
a bunch of collections of singularity images indeed !

I see two main reasons to start damono software. First, Bioconda is great but there are two small limitations: some tools are not there for copyright reasons, or some tools may clash. Remember that bioconda allows you to build an environment with all tools living altogether. Some may be in conflicts. Second, singularity images posted here are there are a great source of inspirations. Yet, I wanted a very simple tool for my users and hide the nitty-gritty details of singularity. In practice, on a cluster, you can get the missing tools in a few seconds. Your system administrator can install singularity and damona and then you can download ready-to-use executable.

Our goal is not to replace existing initiative but just to complement them when
required. 

Installation
============

1. Install singularity: https://syslabs.io/guides/3.0/user-guide/installation.html
2. Install Damono using **pip**. You will need Python 3.X::

    pip install damona --upgrade

Usage
=====


Print the list of images available within Damona collections::

    damona list

Download the one you want to use::

    damona pull fastqc

This will download the container in your ./config/damona directory and create an
executable for you in ~/.config/damona/bin. 

You just need to append your PATH. For instance under Linux, type:

    export PATH=~/config/damona/bin:$PATH

You you can also add in your .profile or .bashrc file for this command to be
permanent.

You are ready to go. Just type this command to use the newly installed container::

    fastqc --help

This tool is pretty common in NGS and can be easily installed. This is more a
toy example than a real example. 


In Damona, we currently provide just a few container. For instance, we provide
an image for R v4.0.2. This is not a NGS tool per se but can be used to build
other container. Besides, you can easily play with R without the need to
interfer with your system::

    damona pull r_4.0.2  # Note the small cap



Roadmap
=========

* handle versioning
* ability to retrieve registry to fill the list of images automatically
* ability to download from other collections


Changelog
=========

========= ====================================================================
Version   Description
========= ====================================================================
0.2.0     first working version of damona to pull image locally with binaries
0.1.1     small update to fix RTD, travis, coveralls
0.1       first release to test feasibility of the project
========= ====================================================================










