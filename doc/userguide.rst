User Guide
##########

Print the list of  containers (from damona or from a remote registry)
---------------------------------------------------------------------

**Damona** itself contains just a few containers. As explained in the motivation, other
projects provide thousands of containers but here we provide containers for
testing and proof of concept. 

By default, **Damona** uses recipes, which can be found in the
https://github.com/damona/damona/recipes directory. In the registry files (see
later for details), we define the URL where images can be downloaded. Some are
on https://cloud.sylabs.io/library/cokelaer collection, which is limited to 10Gb
and therefore will not provide many containers. Others are on external registry
and one can define its own registry for its projects.

To get a list of the available containers in Damona, type::

   damona available-images

You should see the container names and their version. You should also see where
the file is going to be downloaded from.

You can search for specific pattern using::

    damona search qc

This is not a lot indeed. So, we provide a system where you can look for
containers elsewhere on internet. For now, there is only one registry available
on https://biomics.pasteur.fr/salsa/damona (again for demonstration). There, we posted
some containers and a registry.txt file; if you type::

    damona available-images --from-url https://biomics.pasteur.fr/salsa/damona/registry.txt

you will get a list of the images that are available. Anybody can provide a
container on any website with a registry.txt and you will be able to access to
the images.

The latter command can be simplied into ::

    damona available-images --url damona

This is possible by defining alias in the configuration file (in
~/config/damona.cfg as explained in the developer guide)



Download and install an image
-----------------------------

Given the container name an dversion, you can now download a container image as follows::

    damona install fastqc:0.11.9

If there are several version and you just want the latest, remove the tag::

    damona install fastqc

That's it, you should get the image in your config path ~/.config/damona/images
directory. In addition, a binary alias is created in ~/.config/damona/bin

Now, we need to tell you shell where the binaries can be found. You may do it
yourself by changing your PATH environemental variable. We have also a mechanism
in DAMONA using the **activate** command. More about it later but for testing,
you can type::

    damona activate base

And the *fastqc* command should be available::

    fastqc

Note that using the activate command above, your PATH has been changed in your
current shell. 

To install an image/binary, you can also use an external registry (see developer
guide to define your own registry)::

    damona install fastqc:0.11.9 --from-url https://biomics.pasteur.fr/drylab/damona/registry.txt

For this particular website, we have an alias::
 
    damona install fastqc:0.11.9 --from-url damona

You can add aliases in *~/.config/damona/damona.cfg* file.

Different Environments
----------------------

So far, we have downloaded and created aliases in the main **damona**
environment, which is named **base**. It is in  *~/.config/damona*. There, you have two sub-directories: 

* bin
* images

In the *images* directory, we store the singularity containers. In *bin* directory, we create aliases
so as to make the container executables.

Now what about having different environments ? It would be nice to handle
several pipelines in their own environments.

We could quickly test two different versions of a tools and test their impact on an
analysis.::

    damona env --create test1
    damona env --create test2

Now, you need to activate the first one::

    damona activate test1

and install a tool with a given version in this environement::

    damona install fastqc:0.11.9 

And to install it in the *test2* environment::

    damona deactivate
    damona activate test2
    damona install fastqc:0.11.8 --from-url damona

You can activate as many environments as you wish. Calling deactivate will only
deactivate the last activated environment. In works as a Last In First Out mechanism.



Binding directories
--------------------

All binaries created with Damona use this syntax::

    singularity -s exec ${DAMONA_SINGULARITY_OPTIONS} ${DAMONA_PATH}/images/<IMAGE> <EXE> ${1+"$@"}

where EXE is the name of the executable binary, IMAGE the name of the container.
Then, you can see two environmental variable. The DAMONiA_PATH variable must be
defined by you and point to the place where all binaries and images are stored.

This is especially useful would you need to bind a path that is not present in
standard configuration. For example, on a cluster where your admin system set up
a local scratch in /local/scratch, you can tell singularity to look there by
binding this path into your container::

    export DAMONA_SINGULARITY_OPTIONS="-B /local/scratch:/local/scratch"








