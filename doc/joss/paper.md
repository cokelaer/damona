---
title: "Damona: a singularity environment manager for reproducible analysis"
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

# Motivation

Next Sequencing Generation (NGS) [@Goodwin2016] implies complex analysis using pipelines that depends on a plethora of software. A few years ago, setting up a local system to reproduce an analysis was a challenge even for computer scientists. Indeed, one needed to be proficient in several languages. For instance you would nee to compile C/C++ code or set up the correct JAVA or R environments just to cite a few examples. Hours were spent in retrieving the correct source code, days in compilation time, weeks in reproducing analysis. Reproducing the analysis on another operating system would have been even more challenging.

Solutions are now available to help researchers installing reproducible NGS pipelines, and in particular their third-party dependencies. One of them is **conda** [@conda], an open source *package* management system and an *environment* management system. Conda provides pre-compiled releases of a software; they can be installed in different local environments that do not interfer with your system. Thereupon, different communities have emerged using this framework. One of them is **Bioconda** [@Gruning2018], which is dedicated to bioinformatics. A complementary tool is **Singularity** [@Kurtzer2017]; it is a container platform. It allows you to create containers that package your favorite environment and software (even data) in a way that is portable and reproducible. You can build a container locally, copy it elsewhere and run it straightaway (e.g., on a High Performance Computing (HPC) systems). It is a simple flat file that can be shared between environments and guaranteee execution and reproducibility. Note that nothing prevent you from including a conda environment inside a singularity container to speed up the creation of the container (less compilation time).

Bioinformaticians have now all the tools to build reproducible pipelines. In practice, conda environment can also be used to provide a development framework. You can quickly install software in an environment and develop your software in it. Then, you can share your environment for colleagues. It is a quite effective solution to reproduce analysis while moving forward with development. Yet, with the increasing number of tools used in NGS pipelines, pratical issues may arise. A non exhaustive list of examples: impossibility to reproduce an environment, conflicts when installing a software, long time to resolve dependencies. You could have an environment per pipeline but then you need to install common packages several times in different environment.  What if you realise that a tool has a wrong version and you do not want, or cannot update your conda environment. A simple solution consists in providing a singularity container for that specific package and put it in your environment. We could generalise this idea. However, where is the limit? We could pursue the idea and move all the packages from a conda environment within singularity container or the conda environment itself. Then we have a 100% reproducible environment. However, you cannot change it easily. This is not an environment you can deploy iteratively.

This is why we have moved litle by little to a very light conda environment where known-to-cause-problem packages have been shipped into singularity containers. Since we still have the conda environment, we keep its flexibility and ability to update our Python software easily as well. This gives us the flexibility of a conda environment(s) while having the complex packages available as singularity containers. Yet, with increasing number of singularity containers, we need to have aliases and make them available for each environment. 
That's where **Damona** started: a manager for singularity containers. Once a conda environment is used, you can have a **Damona** environment in parallel that will host singularity containers. An environment can be set up for a given analysis. It is then easy to export the containers and share them on another environment. Each developer will adjust the tradeoff between packages installed with conda and containers installed with **Damona** based on its needs.

Our goal is not to replace existing initiative but just to complement them when required. In particular, we designed **Damona** so as to provide the containers required by [Sequana pipelines](https://sequana.readthedocs.io pipelines) [@Cokelaer2017]. We therefore provide some singularities but more as example and proof-of-concept rather than an exhaustive set of singularity containers. **Bioconda** and biocontainer.pro provides such features with thousand of containers already available.

In the following we quickly describe the principle of **Damona** followed by some test cases. 


# Damona to manage singularity containers

This is the egg and chicken paradox. To allow reproducibility you need a tool to
start with. With **Damona**, we have made the choice of using Singularity. Conda is not required to install Damona but strongly recommended. So, one
first need to install Singularity. Instructions from their
[user guide](https://sylabs.io/guides/3.0/user-guide/installation.html) should be sufficient. HPC admistrator can provide the tool for you. 

Then, install **Damona** itself. It is written in Python and available on
[Pypi](https://) website. The following command should install the latest version of the software:

```bash
    pip3 install damona --upgrade
```

The philosophy of Damona is to make life easier both for developers and
end-users. Let us say that a pipeline requires the **salmon** tool (RNA-seq
analysis), then one should just type:

```
    damona install salmon
```

This command first downloads a container with *salmon* installed in it. Then, it is copied into 
a dedicated path that will contain all your images. Under Linux, this will be in /home/user/.config/damona/images. Finally, it created an alias to the executable contained in the recipe. 


This assume the singularity has an executable. We cannot know the name. That's
wy you may have a simple registry with a one-to-one mapping. We could also guess
the name from the name of the container but is not 100% guaranteed. One can
always edit the alias later on. 

Several questions need to be asked at that stage. What is the version of the container ? 
Where is it stored ? What is the alias, What are the list of available
containers. 

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
 

In **Damona** there are three classes of container:

* executables (like the one above)
* environement: for instance, we provide an image for R v4.0.2. This is not a NGS tool per se but can be used to build other containers.
* Set of executables 

# Test cases
## Testing same pipeline with two different version of a third-party tool
## Building several environments in a few seconds
## Updating an entire environment replacing only one file



# Acknowledgments

This work has been supported by the France Génomique Consortium (ANR 10-INBS-09-08).


# References


https://github.com/bdusell/singularity-tutorial
