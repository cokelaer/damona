Developer guide
===============


.. contents:: Table of Contents

Introduction
------------

Damona exposes a few additional commands that are intended for container
developers and are hidden from the standard ``--help`` output.

Build a Singularity image::

    damona build --help

Publish a finished image to Zenodo::

    damona publish --help

.. _dev-config:

Configuration file
------------------

The Damona configuration file lives at ``~/.config/damona/damona.cfg`` and is
created automatically on first use.  It follows the standard
:mod:`configparser` INI format.

A typical file looks like::

    [general]
    verbose=True

    [urls]
    damona=https://biomics.pasteur.fr/salsa/damona/registry.txt

    [zenodo]
    token=APmm6p....
    orcid=0000-0001
    name='Cokelaer, Thomas'
    affiliation='Institut Pasteur'

    [sandbox.zenodo]
    token=FFmbAEhQbb...
    orcid=0000-0001
    name='Cokelaer, Thomas'
    affiliation='Institut Pasteur'

The ``[urls]`` section defines short aliases for external registry URLs.  When
a user runs::

    damona install example --url damona

the alias ``damona`` is replaced by its full URL.  The URL must end with the
file name ``registry.txt`` or ``registry.yaml``.

The ``[zenodo]`` sections are only needed for developers who upload images;
they are not required for normal use.


Publishing images on Zenodo
----------------------------

The goal is to assign a permanent, citable DOI to every container::

    git clone git@github.com/your_fork/damona
    cd damona

Consider the example tool **SOFTWARE**.  Navigate to its recipes directory::

    cd recipes/SOFTWARE

.. warning:: The following commands require a registered Zenodo token and will
   actually create Zenodo records.  Always test with the sandbox first
   (the default) before using ``--production``.

**Case 1 – New tool (no existing Zenodo record):**

Test with the sandbox first (default), then publish for real::

    damona publish SOFTWARE_1.0.0.img               # sandbox — no real DOI
    damona publish SOFTWARE_1.0.0.img --production  # production — permanent DOI

Damona uploads the image, creates a new Zenodo deposit, and then prompts
interactively for the binary names that the container exposes::

    Binary names for 'SOFTWARE' (space or comma separated) [SOFTWARE]: software softtool

The answer is written as a ``binaries:`` field at the top of the generated
``registry.yaml``.  Review the file, then commit and push.

To skip the interactive prompt (e.g. in a script), pass ``--binaries``
directly::

    damona publish SOFTWARE_1.0.0.img --production --binaries "software softtool"

**Case 2 – New version of an existing tool:**

::

    damona publish SOFTWARE_2.0.0.img --production

Damona appends the new release block to the local ``registry.yaml`` and
prompts for any binaries that are **specific to this release** (i.e. not
covered by the top-level ``binaries:`` field)::

    Extra binaries for this release (space or comma separated, empty to skip) []:

Leave the prompt empty if no extra binaries are needed.  If extra binaries
are provided they are written as ``extra_binaries:`` inside the release block.
Pass ``--extra-binaries`` on the command line to skip the prompt.

If the global ``binaries:`` field is currently empty in the registry, a
warning is printed as a reminder to fill it in.

**Case 3 – Re-publishing the same version (updated image):**

If ``SOFTWARE_2.0.0.img`` was already published and you need to replace it
with a corrected build, run ``damona publish --production`` again with the same filename.
Damona detects the existing ``2.0.0`` entry in the local ``registry.yaml``,
comments it out automatically::

    # 2.0.0:
    #   download: https://zenodo.org/record/.../SOFTWARE_2.0.0.img
    #   ...

and then appends the fresh entry below it.  If the old entry had an
``extra_binaries:`` value it is offered as the default for the new entry's
prompt, so no information is lost.

Repository layout
------------------

Recipes are kept in the ``./recipes/`` directory, one sub-directory per tool::

    recipes/
    ├── fastqc/
    │   ├── Singularity.fastqc_0.11.9
    │   └── registry.yaml
    └── salmon/
        ├── Singularity.salmon_1.3.0
        └── registry.yaml

If a tool ships only one recipe, name it::

    Singularity.toolname

For multiple versions::

    Singularity.toolname_x.y.z

Naming conventions
------------------

A valid Singularity recipe file must follow::

    Singularity.NAME_x.y.z
    Singularity.NAME_SUFFIX_x.y.z

The resulting image seen by users will appear as::

    NAME:x.y.z
    NAME_SUFFIX:x.y.z

.. note:: Names may be mixed-case in the recipe but Singularity Hub converts
   them to lowercase.  Always use lowercase when referring to images in
   commands such as ``damona install pkgname:x.y.z``.

Building an image
------------------

Test a recipe locally::

    damona build Singularity.pkgname_x.y.z

This is a thin wrapper around::

    sudo singularity build pkgname_x.y.z.img Singularity.pkgname_x.y.z

You can also build a registered recipe by name::

    damona build fastqc:0.11.9

Specify a custom output path::

    damona build fastqc:0.11.9 --output-name ~/temp.img

Writing Singularity recipes
----------------------------

**Pin the base image version** to avoid silent changes::

    BootStrap: docker
    From: mambaorg/micromamba:1.4.4   # good

rather than::

    BootStrap: docker
    From: mambaorg/micromamba:latest  # avoid

**Recommended** ``%environment`` block to prevent locale warnings::

    %environment
        LANG=C.UTF-8
        LC_ALL=C.UTF-8
        export LANG LC_ALL

Adding a ``%test`` block makes it easy to verify the image after building::

    %test
        command --version

Labels and help sections are optional.

Micromamba-based recipes
-------------------------

The ``library/micromamba`` directory provides a reusable base image.  Use it
to install conda packages without building from scratch::

    Bootstrap: localimage
    From: micromamba_1.5.8.img

    %post
        apt -y update && apt -y upgrade

        export PATH=$PATH:/opt/conda/envs/main/bin/
        export OPTS=" -q -c conda-forge -c bioconda -n main -y "

        micromamba install $OPTS python="3.9"
        micromamba install $OPTS "art==3.19.15"

        micromamba clean --packages -y
        micromamba clean --all -y
        rm -rf /opt/condas/pkg

    %environment
        export PATH=$PATH:/opt/conda/envs/main/bin/

    %runscript
        art_illumina "$@"

Registry format
----------------

Each tool requires a ``registry.yaml`` file.  Two equivalent layouts are
supported:

*Binaries per-release:*

::

    fastqc:
        releases:
          0.11.9:
            download: https://example.com/fastqc_0.11.9.img
            md5sum: abc123...
            binaries: fastqc
          0.11.8:
            download: https://example.com/fastqc_0.11.8.img
            md5sum: def456...
            binaries: fastqc

*Shared binaries (applies to all releases unless overridden):*

::

    fastqc:
        binaries: fastqc
        releases:
          0.11.9:
            download: https://example.com/fastqc_0.11.9.img
            md5sum: abc123...
          0.11.8:
            download: https://example.com/fastqc_0.11.8.img
            md5sum: def456...

When a new release ships additional executables not present in older versions,
declare them with ``extra_binaries:`` inside that release block.  They are
combined with the top-level ``binaries:`` at install time::

    busco:
        binaries: busco
        releases:
          6.0.0:
            download: https://zenodo.org/record/.../busco_6.0.0.img
            md5sum: a24cabbbc9...
            filesize: 730955776
            extra_binaries: miniprot,miniprot_index
          5.4.6:
            download: https://zenodo.org/record/.../busco_5.4.6.img
            md5sum: 9707085637...
            filesize: 546848768

**Marking broken releases:**

If a release is found to be buggy or otherwise unsuitable for new users, mark it
with ``broken: true``. Broken releases are:

- Hidden from ``damona search`` results
- Skipped when auto-selecting the latest version with ``damona install name``
- Still installable via explicit version: ``damona install name:x.y.z`` (with a warning)

This preserves reproducibility (users can still access the version) while
preventing accidental use::

    fastqc:
        binaries: fastqc
        releases:
          0.11.9:
            download: https://zenodo.org/record/.../fastqc_0.11.9.img
            md5sum: abc123...
          0.11.8:
            download: https://zenodo.org/record/.../fastqc_0.11.8.img
            md5sum: def456...
            broken: true  # Hide from search, skip auto-pick

``damona publish`` prompts for ``extra_binaries`` interactively and writes
the field automatically when a non-empty value is given.

The ``download`` value can be:

1. A direct HTTPS URL to a ``.img`` or ``.sif`` file.
2. A Docker Hub reference, e.g. ``docker://biocontainers/hisat2:v2.1.0-2-deb_cv1``.

**Example with a Docker source:**

::

    hisat2:
        releases:
          2.1.0:
            download: docker://biocontainers/hisat2:v2.1.0-2-deb_cv1
            binaries: hisat2 hisat2-build
            md5sum: e680e5ab181e73a8b367693a7bd71098

Where are images stored?
-------------------------

Since December 2021, Damona stores all images with a DOI on
`Zenodo <https://zenodo.org>`_.  Previously some images were hosted on
`Sylabs Cloud Library <https://cloud.sylabs.io/library/cokelaer/damona>`_.

You can always use the bundled offline registry (no internet required) by
passing ``--local-registry-only``::

    damona search fastqc --local-registry-only
    damona install fastqc --local-registry-only

Automatic README generation
-----------------------------

The script ``build_readme.py`` in ``damona/`` parses a ``registry.yaml`` and
produces a standardised ``README.md``.  Run it from the tool's recipes
directory to create or update the README::

    cd recipes/fastqc
    python ../../build_readme.py

Setting up the pre-commit hook
-------------------------------

The repository uses `pre-commit <https://pre-commit.com/>`_ to keep the global
registry up-to-date automatically on every commit::

    pip install pre-commit
    pre-commit install
    git commit .
