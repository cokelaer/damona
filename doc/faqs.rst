FAQs
====

A Fatal error: cannot open file occured but the file is visible
----------------------------------------------------------------

It could be that your file is on a NFS directories, which is not visible in the
container. 

You can fix this by setting the **DAMONA_SINGULARITY_OPTIONS** variable. This
variable can be set to pass any singularity options to all binaries installed by
**Damona**. 

For instance, if you have a NFS mounted directory in /mnt/my_space, you 
can bind it in singularity and therefore DAMONA using (in a bash shell)::

    export DAMONA_SINGULARITY_OPTIONS=" -B /mnt/my_space:/mnt/my_space"

or within fishshell::

    set DAMONA_SINGULARITY_OPTIONS "-B /mnt/my_space:/mnt/my_space"


Why Damona and not conda/mamba ? 
--------------------------------

Damona is not meant to replace conda/bioconda that have a great 
community and a large number of packages available. It is a complementary 
tool that is meant to be super-easy and provide reproducible environments 
as a set of singularity images.

Conda is great but in practice we faced some difficulties. First, 
as a developper using tens or hundreds of binaries for real-life applications,
it was not uncommon to break conda environments when installing a new software. 
Also you can now come back to previous versions it was time-consuming for the team. 
The second common problem we had was the ability to share identical environments 
where software were identical between the different developers to ensure reproducible 
environments and analysis for our customers/users. 

That is where Damona started. We could share images where entire environments
with a set of binaries would be available to all in the exact same way. 

As a developper you can then use conda to try a new or complementary software 
while keeping your core software identical between environments. 



