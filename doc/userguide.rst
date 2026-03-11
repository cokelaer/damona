User Guide
==========


.. contents:: Table of Contents

Getting help
-------------

The **Damona** command-line tool is called ``damona``.  Every command exposes
its own ``--help`` flag::

    damona --help

The list of available commands includes:

.. code-block:: text

    activate      Activate a Damona environment
    clean         Remove orphan images or binaries
    deactivate    Deactivate the current environment
    env           List, create, or delete environments
    export        Export an environment to a bundle or YAML file
    info          Display information about an installed image
    install       Download and install a container image
    list          List available images in the registry
    remove        Uninstall a binary or image
    search        Search the registry for software
    stats         Display statistics about the local installation

For detailed help on any sub-command, append ``--help``::

    damona install --help

Environments
------------

An *environment* in Damona is simply a directory under
``~/.config/damona/envs/`` that contains a ``bin/`` sub-directory.
When an environment is *activated*, its ``bin/`` path is prepended to your
``PATH``, making all installed software immediately available.  All
Singularity images are shared between environments to avoid duplicating large
files on disk.

List environments
~~~~~~~~~~~~~~~~~

Show all environments on the system::

    damona env

When starting fresh, you will see only the **base** environment.  The **base**
environment is reserved and cannot be deleted, but you can install software
into it freely.

Create an environment
~~~~~~~~~~~~~~~~~~~~~

Create a new environment called ``TEST``::

    damona env --create TEST

All environments are created under ``~/.config/damona/envs/``.  After
creation, run ``damona env`` again to confirm it appears in the list.

Activate and deactivate environments
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Activating an environment appends its ``bin/`` directory to your ``PATH``.
Any software installed in that environment then becomes available directly
from the command line::

    damona activate TEST

Verify the active environment::

    damona env

The last line should read::

    Your current env is 'TEST'.

Deactivate when you are done::

    damona deactivate TEST

Environments behave as a **Last-In-First-Out** stack: calling ``deactivate``
without an argument always removes the most recently activated environment::

    damona activate base
    damona activate TEST
    damona deactivate        # removes TEST, base remains active

To deactivate a specific environment by name::

    damona activate base
    damona activate TEST
    damona deactivate base   # removes base, TEST remains active


Software and releases
---------------------

Search for available software
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Damona** ships with a built-in registry of container recipes.  To list all
available images::

   damona search "*" --images-only

Each result shows the container name, its version, and where the image will be
downloaded from.

Search for a specific tool by name::

    damona search fastqc

**Third-party registries** – Anyone can publish containers on the web and
provide a ``registry.txt`` index file.  Point Damona at that file to search
it::

    damona search "*" --url https://biomics.pasteur.fr/salsa/damona/registry.txt

The above URL has a predefined alias called ``damona`` in the default
configuration, so this shorter form is equivalent::

    damona search "*" --url damona

You can add your own aliases in ``~/.config/damona/damona.cfg`` (see the
:ref:`configuration section <dev-config>` in the developer guide).

Download and install a container
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Before installing, activate the environment where you want the software to
live::

    damona activate TEST

Then install the desired container.  Specify an exact version with a colon
separator::

    damona install fastqc:0.11.9

To install the latest available version, omit the tag::

    damona install fastqc

The image is saved to ``~/.config/damona/images/`` and a thin shell-wrapper
binary is created in the active environment's ``bin/`` directory.  The wrapper
looks like::

    #!/bin/sh
    singularity -s exec ${DAMONA_SINGULARITY_OPTIONS} \
        ${DAMONA_PATH}/images/fastqc_0.11.9.img fastqc ${1+"$@"}

After installation the command is immediately available::

    fastqc --version

.. note:: The ``PATH`` change made by ``damona activate`` applies to the
   **current** shell session only.  Open a new terminal and re-activate the
   environment when needed.

Install from an external registry::

    damona install fastqc:0.11.9 --url https://biomics.pasteur.fr/drylab/damona/registry.txt

Or use the short alias::

    damona install fastqc:0.11.9 --url damona

Working with multiple environments
------------------------------------

Damona stores everything under ``~/.config/damona/``:

* ``envs/`` – one sub-directory per environment, each containing a ``bin/``
  folder with wrapper scripts
* ``images/`` – Singularity image files shared across all environments

To test two versions of the same tool side-by-side::

    # Create and populate the first environment
    damona env --create test1
    damona activate test1
    damona install fastqc:0.11.9

    # Switch to the second environment
    damona deactivate
    damona env --create test2
    damona activate test2
    damona install fastqc:0.11.8 --url damona

Both environments now contain their own ``fastqc`` wrapper pointing to the
appropriate image.  Only **one** copy of each image is stored on disk.

Install binaries not listed in the registry
--------------------------------------------

When a container developer registers a tool they list the binaries that should
be installed.  Occasionally a container ships additional executables that are
not yet in the registry.  If you know the binary name, you can install it
directly::

    damona install mummer --binaries show-snps

This creates a wrapper for ``show-snps`` using the ``mummer`` container without
waiting for an official registry update.  If this helps you please consider
opening an issue or a pull request so the registry can be updated for
everyone.

Environmental variables
------------------------

DAMONA_PATH
~~~~~~~~~~~

``DAMONA_PATH`` points to the root directory where Damona stores all of its
data (environments and images).  It is set automatically when you source the
Damona shell script and defaults to ``~/.config/damona/``.

You can point it at a different location (for example a shared network
directory on a cluster)::

    export DAMONA_PATH=/shared/damona

.. _DAMONA_SINGULARITY_OPTIONS:

DAMONA_SINGULARITY_OPTIONS
~~~~~~~~~~~~~~~~~~~~~~~~~~

Every wrapper binary created by Damona uses this template::

    singularity -s exec ${DAMONA_SINGULARITY_OPTIONS} ${DAMONA_PATH}/images/<IMAGE> <EXE> ${1+"$@"}

``DAMONA_SINGULARITY_OPTIONS`` is passed verbatim to ``singularity exec`` and
defaults to an empty string.  Use it to forward any Singularity option to all
binaries at once.

**Tip – X11 display issues:**

The ``-e`` flag tells Singularity to start a clean environment, which unsets
``DISPLAY``.  If graphical tools fail, pass the display through explicitly::

    export DAMONA_SINGULARITY_OPTIONS="-e --env DISPLAY=:1"

**Example – Binding directories:**

On HPC clusters a scratch directory such as ``/local/scratch`` may not be
visible inside the container.  Bind it explicitly::

    export DAMONA_SINGULARITY_OPTIONS="-B /local/scratch:/local/scratch"

Multiple options can be combined in the same string.

