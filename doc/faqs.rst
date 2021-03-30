

A Fatal error: cannot open file occured but the file is visible
----------------------------------------------------------------

It could be that your file is on a NFS directories, which is not visible in the
container. 

You can fix this by setting the DAMONA_SINGULARITY_OPTIONS variable. This
variable can be set to pass any singularity options to all binaries installed by
DAMONA. 

For instance, if you have a NFS mounted directory in /mnt/my_space, you can binf
it in singularity and therefore DAMONA using::

    export DAMONA_SINGULARITY_OPTIONS=" -B /mnt/my_space:/mnt/my_space"
