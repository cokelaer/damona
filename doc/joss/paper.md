---
title: "Damona: a singularity environment manager for developers and end-users"
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

Next Sequencing Generation (NGS) [@Goodwin2016] implies complex analysis using pipelines that
depends on a plethora of software. A few years ago, setting up a local system to
reproduce an analysis was a challenge even for computer scientists. Indeed, one
needed to be proficient in several languages to compile C/C++ code,
set up the correct JAVA or R environment, etc. Hours were spent in retrieving
the correct source code, days in compilation time, weeks in reproducing analysis. Indeed, one recurrent issue in research being the ability to reproduce an existing results, which was most probably performed in a different environment. Nowadays, many solutions are available to install reproducible NGS pipelines.
First, the **conda** software manager allows to create environment where compiled version of a software can be installed. More specifically, the **Bioconda** [Gruning2018] community has offered thousands of pre-compiled bioinformatics software on their channel using the conda package manager. Second, reproducible containers can encapsulate
those software within a container based on Docker or Singularity technologies [@Kurtzer2017]. Bioconda even provide docker and singularity containers of each compiled tool.

Bioinformaticians have now all the tools to build reproducible pipelines. There
is still a problem: maintenace. How to provide pipelines that are reproducible
while allowing those tools to evolve. How to help your end-users (e.g.
bio-analysts) to easily install your pipelines. 

For the first question, we use
conda environments. Once created, we install the
third-party librairies and our main software. Yet, after 5 or 10 pipelines are
installed you face a general issue of conflict between dependencies. You could
create one environment per pipeline but this is a burden for maintainer. Setting
new environement on different account has shown some limtations as well in
lacking the ability to reinstall the exact same set of software version. 
Once hundreds of packages are installed, conflict may happen or dependencies not
resolved. Conda is great, Bioconda as well but sometimes it is not the best
solution. Another independent issue is that two versions of the same software 
cannot be installed at the same time (e.g. the newest overwrite a file 
required by the oldest). This is details of course but we have reached 
a level where reproducibility is in the details. An alternative is to provide a
singularity per file. Now we are very modular but too modular. A solution for reproducibility
consists in creating a single container with all your tools inside. This is nice
but with such solution you lack the flexibility of iterating on your development
quickly. Another solution is to have both. One conda environment where the minimal set of
tools is installed, and more complex software that are know to cause problem can
be put in container and transformed into executable. 


This is the choice we have made: a conda environment where our main python
software lives and a set of singularity, each of them having its own life. This
way, the image are alawys available and therefore reproducible and the pipelines
and main software can still move and evolve with time. For reproducility, we
then just need the version of the main software and the singularity images. 

End-users have an easier life as well. No need to install hundreds of software
from conda, just the essential ones or the missing ones.

This can be done from the developer and user sides with actual tools. Yet, 

I see two main reasons to start damona software. First, Bioconda is great but there are two small limitations: some tools are not there or installing two tools may be impossible due to conflits; those conflicts may be long to untangle. Remember that bioconda allows you to build an environment with all tools living altogether. Some may be in conflicts. Second, singularity images posted here are there are a great source of inspirations. Yet, I wanted a very simple tool for my users and hide the nitty-gritty details of singularity. In practice, on a cluster, you can get the missing tools in a few seconds. Your system administrator can install singularity and damona and then you can download ready-to-use executables.

Our goal is not to replace existing initiative but just to complement them when required. In particular, we designed damona so as to provide the executables required by sequana.readthedocs.io pipelines


# Installation, usage, reproducibilty

This is the egg and chicken paradox. To allow reproducibility you need a tool to
start with. With Damona, we've made the choice of using Singularity. So, one
first need to install the software following instructinos from their
[user guide](https://sylabs.io/guides/3.0/user-guide/installation.html).

Then, install **Damona** itself. It is written in Python and avaiable on
[Pypi](https://) website. This should install the software:

```bash
    pip install damona --upgrade
```

The philosophy of Damona is to make life easier both for developers and
end-users. Let us say that a pipeline requires the **salmon** tool (RNA-seq
analys), then one should just type:

```
    damona install salmon
```

This commands downloads the container, copy it in a DAMONA/images directory and set
up an alias (executable) for you in DAMONA/bin directory. DAMONA being set to
/home/user/config/damona under Linux environment.

Damona project was motivated by the growing number of NGS pipelines available in
Sequana [Cokelaer2017] and the third-party dependencies.
ncies

Print the list of images available within Damona collections:
```
    damona list
```
Download the one you want to use:
```
    damona install fastqc:0.11.9
```
This will download the container in your ./config/damona directory and create an executable for you in ~/.config/damona/bin.

You just need to append your PATH. For instance under Linux, type:

    export PATH=~/config/damona/bin:$PATH
 

In damona there are three classes of container:

* executables (like the one above)
* environement: for instance, we provide an image for R v4.0.2. This is not a NGS tool per se but can be used to build other containers.
* Set of executables 


# Acknowledgments

We acknowledge contributions from ....


# References


https://github.com/bdusell/singularity-tutorial
