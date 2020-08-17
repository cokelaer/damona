Relation between images
=======================

This image shows some examples of relations between containers.

We have three classes of containers in **damona**. The conda_4.7.12 for example
is an *environment* that allows us to build *executables* such as salmon,
fastqc, etc. A third class is the *set of executables*. This will create as many
executables as the developer provided in the registry.yaml file.

Nodes in red are hosted on singularity-hub 
Nodes in yellow are images provided by singularity as images to build on.
White nodes are in the default distribution of Damona (will be limited to only a
few containers) and available on sylabs.io cloud to demonstrate the interest of
Damona for scientific projects.

In **Damona** we have 3 types of images: exe (executable), env (environment) and
set (set of executables). They are represented as white circles, diamond or orange polygons

.. graphviz::

    digraph foo {
        "r_4.0.2" [style=filled color=red shape="diamond"];
        "r_3.6.3" [style=filled color=red shape="diamond"];
        "ubuntu:16.04 (docker)" [style=filled color=yellow];
        "ubuntu:20.04 (docker)" [style=filled color=yellow];
        "sequana:0.9.1" [style=filled shape=diamond];
        "conda_4.7.12" [ shape=diamond];
        "sequana_tools:0.9.0" [style="filled" color="orange" shape=octagon];
        "centos:7 (docker)" [style=filled color=yellow];
        "ubuntu:16.04 (docker)" -> "conda_4.7.12";
        "ubuntu:16.04 (docker)" -> "r_3.6.3";
        "ubuntu:16.04 (docker)" -> "r_4.0.2";
        "ubuntu:20.04 (docker)" -> "graphviz:2.43.0";
        "conda_4.7.12" -> "kraken_1.1";
        "conda_4.7.12" -> "sequana_tools:0.9.0";
        "conda_4.7.12" -> "kraken_2.0.9";
        "conda_4.7.12" -> "prokka:1.14.5";
        "conda_4.7.12" -> "salmon:1.3.0";
        "conda_4.7.12" -> "gffread:0.12.1";
        "conda_4.7.12" -> "sequana:0.9.1";
        "sequana:0.9.1" -> "sequana_fastac:1.0.0";
        "sequana:0.9.1" -> "sequana_demultiplex:1.0.0";
        "r_4.0.2" -> "rnadiff:1.7.0";
        "centos:7 (docker)" -> bcl2fastq;
        "centos:7 (docker)" -> "damona:0.3.0";
        "centos:7 (docker)" -> "fastqc:0.11.8";
        "centos:7 (docker)" -> "fastqc:0.11.9";
    }




