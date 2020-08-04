---
title: "Damona: a one command installer for sequana pipelines"
tags:
  - singularity
  - python
  - reproducibility
authors:
 - name: Thomas Cokelaer
   orcid: 0000-0001-6286-1138
   affiliation: "1,2"
affiliations:
 - name: "Hub de Bioinformatique et Biostatistique – Département Biologie Computationnelle, Institut Pasteur, USR 3756 CNRS, Paris, France"
   index: 1
 - name: "Plate-forme Technologique Biomics – Centre de Ressources et Recherches Technologiques (C2RT), Institut Pasteur, Paris, France"
   index: 2



date: 2 August 2020
bibliography: paper.bib
---

# Overview

Damona is a collections of singularity recipes that can be used to build software used in NGS pipelines. It provides a simple excutable to download the images locally and use executable straightaway. 

Why another collections or tools to provide NGS images ? There is bioconda, and a bunch of collections of singularity images indeed !

I see two main reasons to start damona software. First, Bioconda is great but there are two small limitations: some tools are not there or installing two tools may be impossible due to conflits; those conflicts may be long to untangle. Remember that bioconda allows you to build an environment with all tools living altogether. Some may be in conflicts. Second, singularity images posted here are there are a great source of inspirations. Yet, I wanted a very simple tool for my users and hide the nitty-gritty details of singularity. In practice, on a cluster, you can get the missing tools in a few seconds. Your system administrator can install singularity and damona and then you can download ready-to-use executables.

Our goal is not to replace existing initiative but just to complement them when required. In particular, we designed damona so as to provide the executables required by sequana.readthedocs.io pipelines


# Installation, usage, reproducibilty

Install singularity: https://sylabs.io/guides/3.0/user-guide/installation.html

Install Damona using pip. You will need Python 3.X::

    pip install damona --upgrade

The dependencies of Damona are pure python so it should be straightfoward.

Print the list of images available within Damona collections:

    damona list

Download the one you want to use:

    damona pull fastqc:0.11.9

This will download the container in your ./config/damona directory and create an executable for you in ~/.config/damona/bin.

You just need to append your PATH. For instance under Linux, type:

    export PATH=~/config/damona/bin:$PATH
 
You you can also add in your .profile or .bashrc file for this command to be permanent.

You are ready to go. Just type this command to use the newly installed container:

    fastqc --help

In damona there are three classes of container:

* executables (like the one above)
* environement: for instance, we provide an image for R v4.0.2. This is not a NGS tool per se but can be used to build other containers.
* Set of executables 


# Acknowledgments

We acknowledge contributions from ....


# References


https://github.com/bdusell/singularity-tutorial
