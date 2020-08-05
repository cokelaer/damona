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

Yet, Bioconda may have limitations for end-users. One of them is that two tools may be impossible to cohabit or slow to install due to difficulties in resolving their dependencies. Second, singularity images posted here and there are a great source of inspirations. Yet, I wanted a very simple tool both for developers that wish to offer an easy installation and for users to whom we try to hide all the nitty-gritty details of installing third-party librairies.

Our goal is not to replace existing initiative but just to complement them when
required. In particular, we designed **damona** so as to provide the executables
required by `Sequana <sequana.readthedocs.io>`_ pipelines.

We will therefore maintain damona in the context of Sequana project. Yet,
**Damona** may be useful for others developers who wish to have a quick and easy
solution for their users when they need to install third-party libraries

Installation
============

The is the egg and chicken paradox. To get reproducible container with
singularity, at some point you ned to install singularity itself. That the first
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

Print the list of images available within **Damona** collections::

    damona list

Download the one you want to use::

    damona install fastqc:0.11.9

This will download the container in your ./config/damona directory and create an
executable for you in ~/.config/damona/bin. 

You just need to append your PATH. For instance under Linux, type:

    export PATH=~/config/damona/bin:$PATH

That's it. You have downloaded a reproducible container of fastqc tool. 

Check that you have not installed another version::

    which fastqc

More information in the User Guide. 



Changelog
=========

========= ====================================================================
Version   Description
========= ====================================================================
0.3.1     * add gffread recipe
0.3.0     * A stable version with documentation and >95% coverage read-yto-use
0.2.3     * add new recipes (rnadiff) 
0.2.2     * Download latest if no version provided
          * include *build* command to build image locally
0.2.1     fixed manifest
0.2.0     first working version of damona to pull image locally with binaries
0.1.1     small update to fix RTD, travis, coveralls
0.1       first release to test feasibility of the project
========= ====================================================================










