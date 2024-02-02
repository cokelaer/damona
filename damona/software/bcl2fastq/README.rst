In order to build this recipes, you must have your own license of bcl2fastq by
downloading and agreeing to the terms for your user license. We cannot provide
the RPM or source even though they are available for free.

This can be done on Illumina website in the download section you should find the
RPM link to download bcl2fastq2.20 RPM file.

Once you have the RPM, copy it in this directory and call it *bcl2fastq.rpm*

To build this singularity container yourself::

    mkdir temp
    cd temp
    # copy the bcl2fastq RPM file that you have downloaded and create a symbolic link to it ::

    ln -s YOUR.rpm bcl2fastq.rpm
    wget https://raw.githubusercontent.com/cokelaer/damona/master/damona/recipes/bcl2fastq/Singularity.bcl2fastq_2.20.0
    damona build Singularity.bcl2fastq_2.20.0

    # or
    sudo singularity build bcl2fastq_2.20.0.img Singularity.bcl2fastq_2.20.0

That's it you should have a file called bcl2fastq_2.20.0.img this is your
container. You can create a binary called **bcl2fastq** and place it so that
your system sees it. This binary should be executable.

    singularity run PATH_TO_IMAGE.img ${1+"$@"}
