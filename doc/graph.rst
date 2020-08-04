Relation between images
=======================


.. graphviz::

    digraph foo {
        bcl2fastq;
        fastqc ;
        "r_4.0.2" ;
        "r_3.7.3" ;
        "conda_4.7.12" -> "kraken_1.1";
        "conda_4.7.12" -> "kraken_2.0";
        "conda_4.7.12" -> "prokka";
    }




