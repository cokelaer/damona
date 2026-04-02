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


.. image:: https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C3.11%20%7C3.12-blue.svg
    :target: https://pypi.python.org/pypi/damona
    :alt: Python 3.9 | 3.10 | 3.11 | 3.12

.. image:: https://img.shields.io/github/issues/cokelaer/damona.svg
    :target: https://github.com/cokelaer/damona/issues
    :alt: GitHub Issues

:Python version: Python 3.9, 3.10, 3.11, 3.12
:Source: `https://github.com/cokelaer/damona <https://github.com/cokelaer/damona/>`__
:Documentation: `https://damona.readthedocs.io <https://damona.readthedocs.io>`__
:Issues: `https://github.com/cokelaer/damona/issues <https://github.com/cokelaer/damona/issues>`__
:Platform: Linux with bash, zsh, or fish shell

Overview
========


.. image:: https://raw.githubusercontent.com/cokelaer/damona/refs/heads/main/doc/damona_logo.png
   :target: https://raw.githubusercontent.com/cokelaer/damona/refs/heads/main/doc/damona_logo.png
   :align: right
   :alt: logo
   :width: 300px


**Damona** is a conda-style package and environment manager built on top of
`Apptainer/Singularity <https://apptainer.org>`_ containers. It lets you
install bioinformatics (and other) tools as isolated containers, manage
multiple versions side-by-side, and run them **exactly like any other
command-line tool** — with no dependency conflicts and no root privileges
required.

Think of Damona as *conda for Singularity images*: the same familiar
``create / activate / install`` workflow you already know, but with the
rock-solid isolation and reproducibility that containers provide.

.. note::  As of Apr. 2026, **Damona** ships 133 containers (206 versions),
           providing **731 unique ready-to-use binaries**.



Why Damona?
===========

Managing scientific software is notoriously painful:

- Conda environments break when incompatible packages are installed together.
- Raw Singularity/Apptainer requires verbose ``singularity exec`` invocations
  and manual management of image files.
- Docker is unavailable or restricted on most HPC clusters.

**Damona solves all three problems at once:**

+----------------------------------------------+-------+-------+--------+
| Feature                                      | Conda | Singu-| Damona |
|                                              |       | larity|        |
+==============================================+=======+=======+========+
| Familiar install/activate workflow           | ✔     | ✗     | ✔      |
+----------------------------------------------+-------+-------+--------+
| Tools callable as plain commands             | ✔     | ✗     | ✔      |
+----------------------------------------------+-------+-------+--------+
| Full container isolation (no dep. conflicts) | ✗     | ✔     | ✔      |
+----------------------------------------------+-------+-------+--------+
| No root required                             | ✔     | ✔     | ✔      |
+----------------------------------------------+-------+-------+--------+
| Works on HPC/clusters without Docker         | ✔     | ✔     | ✔      |
+----------------------------------------------+-------+-------+--------+
| Multiple tool versions in separate envs      | ✔     | ✗     | ✔      |
+----------------------------------------------+-------+-------+--------+
| Images shared across environments            | ✗     | ✗     | ✔      |
+----------------------------------------------+-------+-------+--------+
| Central + custom registries                  | ✔     | ✗     | ✔      |
+----------------------------------------------+-------+-------+--------+

Key strengths at a glance
--------------------------

* **One command to install** — ``damona install bwa`` downloads the container
  *and* creates a wrapper script so that ``bwa`` just works in your shell.
* **Zero dependency conflicts** — every tool runs inside its own container,
  completely isolated from everything else on the system.
* **No root, no Docker** — Apptainer/Singularity runs fully unprivileged,
  making Damona ideal for shared HPC clusters where Docker is not available.
* **Multiple versions, one system** — need BWA 0.7.17 in one pipeline and
  BWA 0.7.18 in another? Create two Damona environments and switch instantly.
* **Images are shared** — re-installing a tool in a second environment reuses
  the already-downloaded image, saving disk space and time.
* **Reproducible by design** — pin exact versions in an environment file and
  export/import it to reproduce results anywhere.
* **Custom registries** — host your own registry to distribute in-house
  containers to your team, just like a private conda channel.


Installation
============

**Step 1 — Install Apptainer**

Damona is a manager for Apptainer/Singularity images, so Apptainer must be
present on your system first. Follow the official
`Apptainer installation guide <https://apptainer.org/docs/admin/main/installation.html>`_,
or — if you already use conda — install it with::

    conda install -c conda-forge apptainer

**Step 2 — Install Damona**

::

    pip install damona

**Step 3 — Initialise Damona**

Run ``damona`` once to create the configuration directory and shell helpers::

    damona

Follow the on-screen instructions. To make the shell integration permanent,
add **one** of the following lines to your shell start-up file:

*bash* — add to ``~/.bashrc``::

    source ~/.config/damona/damona.sh

*zsh* — add to ``~/.zshrc``::

    source ~/.config/damona/damona.zsh

*fish* — add to ``~/.config/fish/config.fish``::

    source ~/.config/damona/damona.fish

Then **open a new shell** and run ``damona`` again. You should see the help
screen:

.. image::  https://raw.githubusercontent.com/cokelaer/damona/refs/heads/main/doc/_static/cli.png

Quick Start
===========

The full workflow takes under a minute:

.. code-block:: bash

    # 1. Create a named environment
    damona create TEST

    # 2. Activate it (installed tools go here)
    damona activate TEST

    # 3. Install a tool — container + wrapper created automatically
    damona install fastqc:0.11.9

    # 4. Use it just like any other command
    fastqc --help

    # 5. Rename or remove the environment when you're done
    damona rename TEST --new-name prod
    damona remove prod

For more examples see the `User Guide <https://damona.readthedocs.io>`_.

Example without conda (pyenv + minimap2)
-----------------------------------------

If you manage Python with `pyenv <https://github.com/pyenv/pyenv>`_ instead of
conda, the workflow is identical — Damona only requires Python ≥ 3.9 and
Apptainer.

.. code-block:: bash

    # --- Prerequisites ---------------------------------------------------
    # 1. Install Apptainer (once, system-wide or via your package manager).
    #    On Debian/Ubuntu:
    sudo apt-get install -y apptainer
    #    Or follow https://apptainer.org/docs/admin/main/installation.html

    # --- Python environment ----------------------------------------------
    # 2. Create and activate a pyenv virtualenv with Python 3.10
    pyenv install 3.10.14          # skip if already installed
    pyenv virtualenv 3.10.14 damona-env
    pyenv activate damona-env

    # 3. Install Damona
    pip install damona

    # --- First-time initialisation ---------------------------------------
    # 4. Run once to create the configuration directory and shell helpers
    damona

    # 5. Add the shell integration to your start-up file (bash example):
    echo 'source ~/.config/damona/damona.sh' >> ~/.bashrc
    source ~/.bashrc

    # --- Install minimap2 ------------------------------------------------
    # 6. Create and activate a Damona environment
    damona create my-env
    damona activate my-env

    # 7. Install minimap2 — the container is downloaded automatically
    damona install minimap2:2.24.0

    # 8. Use it like any other command
    minimap2 --version

Motivation
==========

`Conda/Bioconda <https://bioconda.github.io>`_ is excellent for distributing
pre-compiled scientific software, but dependency conflicts are a real-world
problem: installing one package can silently break another, and rebuilding
environments is time-consuming.

`Singularity/Apptainer <https://apptainer.org>`_ solves the isolation problem
perfectly — each image is self-contained and reproducible — but using it
directly requires verbose ``singularity exec`` commands and manual bookkeeping
of image files and wrapper scripts.

**Damona bridges the gap**: it wraps Singularity images in the familiar
conda-style environment model so that containers are as easy to install,
activate, and use as conda packages, while retaining full container isolation
and reproducibility.

Damona was originally developed for the
`Sequana project <https://sequana.readthedocs.io>`_, but it is completely
general-purpose and can be used to distribute any Singularity-compatible
software.


Commands (Full CLI Reference)
=============================

Run ``damona --help`` to see all available commands::

    Environment management:
      create      Create a new environment
      remove      Remove an environment and all its binaries.
      rename      Rename an existing environment.
      env         List all environments with their size and binary counts.
      activate    Activate a damona environment.
      deactivate  Deactivate the current Damona environment.

    Package management:
      install     Download and install an image and its binaries into the active environment.
      uninstall   Uninstall a binary or an image from an environment.
      clean       Find and remove orphaned images and binaries across all environments.
      export      Export an environment as a YAML file or a tar bundle.
      info        Show images and binaries installed in an environment.

    Registry:
      search      Search the registry for a container image or binary.
      list        List all containers available in the local registry.
      stats       Show registry statistics and local installation summary.

    Developer tools:
      check    Check that all binaries in a built image are functional.
      build    Build a Singularity image from a local recipe, a Damona recipe, or a Docker image.                                            catalog  Show a developer overview: latest version, size, and base image for every container.


For command-specific help (e.g. ``install``)::

    damona install --help


1. List available environments
-------------------------------

By default there is one environment called **base**. Unlike conda's **base**,
it is not essential and may be altered freely (but it cannot be removed or
re-created). List all environments with::

    damona env

2. Create environments
-----------------------

All environments are stored in *~/.config/damona/envs/*. Create a new one::

    damona create TEST

Verify it was created::

    damona env

The last line should confirm that **TEST** is the current environment.

3. Activate and deactivate environments
----------------------------------------

Activating an environment appends its *bin* directory to your ``$PATH``::

    damona activate TEST
    damona env        # confirms TEST is active

Deactivating removes it from ``$PATH``::

    damona deactivate TEST

Multiple environments can be active simultaneously; they follow a
Last-In-First-Out order when deactivated without a name::

    damona activate base
    damona activate TEST
    damona deactivate           # removes TEST (last activated)
    damona deactivate base      # removes base by name

4. Install a tool
------------------

With the target environment active, install any available package::

    damona install fastqc:0.11.9

Damona downloads the Singularity image, registers it in
*~/.config/damona/images* (shared by all environments), and creates a
wrapper script so that ``fastqc`` is available as a plain command.

5. Inspect an environment
--------------------------

List the binaries installed in an environment together with the underlying
images::

    damona info TEST

6. Search the registry
-----------------------

Search for available packages::

    damona search PATTERN

Search an external registry (e.g. the official Damona registry)::

    damona search fastqc --url damona

The ``damona`` URL alias is pre-configured in
*~/.config/damona/damona.cfg*. You can add your own registry URLs there to
distribute in-house containers.

7. Combine multiple environments
----------------------------------

Images are shared across environments, so re-using an already-downloaded
image in a new environment is instant and costs no extra disk space::

    damona create test1
    damona activate test1
    damona install fastqc:0.11.9   # reuses the cached image

Activate several environments at once to mix tool sets::

    damona activate base
    damona activate test1

For more details see the `User Guide <https://damona.readthedocs.io>`_ and
the `Developer Guide <https://damona.readthedocs.io>`_.


Contributors
============

Maintaining Damona would not have been possible without users and contributors.
Each contribution has been an encouragement to pursue this project. Thanks to all:

.. image:: https://contrib.rocks/image?repo=cokelaer/damona
    :target: https://github.com/cokelaer/damona/graphs/contributors


Changelog
=========

From version 0.16 onwards, we will not mention the new software and their versions
but only changes made to the code itself. Entire list of software is available using
the command::

    damona list

========= ========================================================================
Version   Description
========= ========================================================================
0.19.2    * CHANGED faster `damona check <IMG>`
          * UPDATED sequana 0.21 image
0.19.1    * CHANGED `damona upload` to `damona publish`
          * NEW: new busco 6.0.0
0.19.0    * ADDED: isoquant container (scratch-built, no micromamba)
          * FIXED: Zenodo upload now uses Bearer token authentication header
            instead of ``access_token`` query parameter (required by the new
            Zenodo InvenioRDM API)
          * CHANGED: upload always creates a new independent deposit instead of
            versioning an existing one, so any developer can contribute a new
            release regardless of who originally created the record
          * REMOVED: top-level ``doi`` field from registry (was the Zenodo
            concept DOI — unused and no longer meaningful with independent
            deposits)
          * IMPROVED: ``damona stats --include-downloads`` now prints results
            line-by-line as they arrive instead of waiting for all requests to
            complete
0.18.0    * NEW command: catalog
          * DECREASE fott print of repeatmasker
0.17.2    * ADDED sniffles, macs3, verkho
          * IMPROVED: new damona command for developers: build and check
0.17.1    * RENAMED: ``delete`` command renamed to ``remove``
          * RENAMED: ``remove`` command renamed to ``uninstall``
          * RENAMED: ``--logger`` option renamed to ``--log-level``
          * RENAMED: ``--remove`` flag in ``clean`` renamed to ``--do-remove``
          * IMPROVED: CLI commands grouped into Environment management, Package
            management, and Registry sections
          * IMPROVED: simplified ORCID parsing in zenodo upload
          * ADDED: bedops
0.17.0    * IMPROVED: CLI output now uses rich tables and panels
          * IMPROVED: auto-update shell config files (bash/zsh/fish) on startup
          * FIXED: fish shell activation and PATH propagation
          * FIXED: subprocess-based shell detection replacing env-variable approach
          * FIXED: first-run exit code no longer causes CI failures
          * BUILD: remove sudo requirement from singularity build commands
          * BUILD: add dependency caching to CI workflows
0.16.0    * update precommit to create global registry automatically
0.15.2    * ADDED: purge_haplotigs
          * FIXED: access to online registry (Default behaviour)
0.15.1    * using loguru (tentative). Update to have real 0.15.X version
            0.15.0 is unfortunately is not uploading on pypi....
0.15.0    * biocontainers integrated
          * Fix #35 to have a common registry online. no need to update damona
            anymore.
0.14.7    * ADDED rseqc 5.0.4
          * UPDATED sequana_tools 0.19.1
0.14.6    * UPDATED freebayes to 1.3.9
          * ADDED meme suite 5.5.3
0.14.5    * UPDATED pyproject to use poetry2.0 and drop py3.8 support for py3.12
          * ADDED wget 1.25.4, chromap 0.2.7, qc3c 0.5.0 and pairtools 1.1.2
0.14.4    * UPDATE quast 5.3
          * ADDED RNAfold 2.7.0
          * ADDED pilon 1.24
          * ADDED Mauve 2.4.0
0.14.3    * ADDED pecat 0.0.3, necat 0.0.1, sequana_coverage 0.18
          * ADDED: bcftools 1.16, khmer 2.1.1  tRNAscan_SE 2.0.12
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
          * ADD nanopolish and remove nanopolish from sequana_tools binaries
0.9.1     * ADD hmmer 3.2.2, trinotate 4.0.1, transdecode 5.7.0, trinity 2.15.1
          * UPDATE bioconvert 1.1.0, bowtie2 2.5.1
0.9.0     * refactorise the command 'env' by splitting into dedicated subcommands
            create, delete, rename. add progress bar when downloading container
          * NEW micromamba image to work as a localimage
          * NEW sequana_minimal package to hold common tools (bwa, samtools,
            kraken, etc)
          * NEW ivar, pangolin, nextclade, subread, mafft packages
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
            - Simplification of the registries
            - New command to build images from local recipes or dockerhub entries.
            - Install command can now install local container.
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
