FAQs
====

A Fatal error: cannot open file occurred but the file is visible
-----------------------------------------------------------------

This is most likely caused by the file residing on an NFS (network file
system) mount that is not visible inside the container.

Fix it by setting the ``DAMONA_SINGULARITY_OPTIONS`` environment variable to
bind the NFS mount into the container:

In a **bash** or **zsh** shell::

    export DAMONA_SINGULARITY_OPTIONS="-B /mnt/my_space:/mnt/my_space"

In a **fish** shell::

    set DAMONA_SINGULARITY_OPTIONS "-B /mnt/my_space:/mnt/my_space"

See the :ref:`DAMONA_SINGULARITY_OPTIONS` section of the user guide for more
details and additional examples.

Why Damona and not conda/mamba?
--------------------------------

Damona is **not** a replacement for conda/bioconda – it is a complementary
tool with a different focus:

- **Reproducibility** – Singularity images are immutable; running the same
  container on two different machines always produces the same result.
- **Isolation** – Containers do not share libraries with the host system, so
  there are no dependency conflicts between tools.
- **HPC-friendly** – Singularity/Apptainer does not require root privileges
  and is widely available on computing clusters where Docker is not permitted.
- **Easy sharing** – A bundle file created with ``damona export`` can be given
  to a colleague who can recreate the exact same environment with
  ``damona env --from-bundle``.

In practice many bioinformatics teams use *both*: conda for exploratory work
and Damona for the stable, shared analysis pipelines that need to be
reproducible over time.

Useful related projects
------------------------

* `StaPH-B Docker images <https://hub.docker.com/u/staphb>`_ – a community
  effort providing Docker images for public-health bioinformatics tools.

