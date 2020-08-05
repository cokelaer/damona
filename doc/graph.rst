Relation between images
=======================

This image shows some examples of relations between containers.

We have three classes of containers in **damona**. The conda_4.7.12 for example
is an *environment* that allows us to build *executables* such as salmon,
fastqc, etc. A third class is the *set of executables*. This will create as many
executables as the developer provided in the registry.yaml file.

.. graphviz::

    digraph foo {
        bcl2fastq;
        "fastqc:0.11.9";
        "r_4.0.2" ;
        "r_3.7.3" ;
        "r_4.0.2" -> "rnadiff:1.7.0";
        "conda_4.7.12" -> "kraken_1.1";
        "conda_4.7.12" -> "kraken_2.0";
        "conda_4.7.12" -> "prokka:1.14.5";
        "conda_4.7.12" -> "salmon:1.3.0";
    }




