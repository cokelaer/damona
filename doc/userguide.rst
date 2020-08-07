User Guide
##########

Print the list of  containers (from damona or from a remote registry)
---------------------------------------------------------------------

**Damona** contains just a few containers. As explained in the motivation, other
projects provide thousands of containers but here we provide containers for
testing and proof of concept. 

By default, **Damona** will look for containers on 
https://cloud.sylabs.io/library/cokelaer collection, which is limited to 10Gb
and therefore will not provide many containers.

To get a list of the available containers, just type::

   damona list 

You should see the container names and their version::

   conda:4.7.12, damona:0.3.0, fastqc:0.11.9, kraken:1.1, kraken:2.0.9, prokka:1.14.5, r:3.6.3, r:4.0.2, rnadiff:1.7.0, salmon:1.3.0

You can filter by selecting a specific pattern::

    damona list --pattern qc

This is not a lot indeed. So, we provide a system where you can look for
containers elsewhere on internet. For now, there is only one registry available
on https://biomics.pasteur.fr/drylab/damona (again for demonstration). There, we posted
some containers and a registry.txt file; if you type::

    damona list --from-url https://biomics.pasteur.fr/drylab/damona/registry.txt

you will get a list of the images that are available. Anybody can provide a
container on any website with a registry.txt and you will be able to access to
the images. 


Download and install an image
-----------------------------

Given the container name an dversion, you can now download a container image as follows::

    damona install fastqc:0.11.9

If there are several version and you just want the latest, remove the tag::

    damona install fastqc

That's it, you should get the image in your config path ~/.config/damona/images
directory. In addition, a binary alias is created in ~/.config/damona/bin

The container is a Singularity container. **Damona** is just a simple wrapper
around Singularity. For example::

    singularity run name.img fastqc

Should run the container and launch the executable *fastqc* to be found inside.
With Damona, we provide a simple framework that ease the life of the developer
and user. We have indeed a simple registry system stored with each recipe. When
required, we create a binary in ~/.config/damona/bin/fastqc named after the recipe name.

All you need to do is call the executable from this directory. Even better, set
your environment to look for executables in ~/.config/damona/bin/ For example::

    export PATH=~/.config/damona/bin/:$PATH

and you are ready do go.

If you are using a registry.txt from a remote URL, it works in the same way::


    damona install fastqc:0.11.9 --from-url https://biomics.pasteur.fr/drylab/damona/registry.txt

For this particular website, we have an alias::
 
    damona install fastqc:0.11.9 --from-url damona

You can add aliases in *~/.config/damona/damona.cfg* file.

Different Environments
----------------------

So far, we have downloaded and created aliases in the main **damona**, which is
by default in *~/.config/damona*. There, you have two sub-directories: 

* bin
* images

In the *images* we store the singularity containers. In *bin* we create aliases
so as to make the container executables.

Now what about having different environements ? It would be nice to handle
several pipelines in their own environments.

We could quickly test two different version a tools on their impact on an
analysis.::

    damona env --create test1
    damona env --create test2

Now, you need to activate the first one::

    damona activate test1

Here, unfortunately, this feature is not yet implemented so you need to do it
yourself. Under bash unix type you can type e.g.,::

    export DAMONA_ENV="~/.config/damona/envs/test1"

Now you can install a tool with a given version in this environement::

    export DAMONA_ENV="~/.config/damona/envs/test1"
    damone install fastqc:0.11.9 

    export DAMONA_ENV="~/.config/damona/envs/test2"
    damona install fastqc:0.11.8 --from-url damona

