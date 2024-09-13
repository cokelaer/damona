User Guide
==========


.. contents:: Table of Contents

Getting help
-------------

The Damona standalone is called damona. It has a documentation that should suffice for most users.

The main documentation is obtained using::

    damona --help

where you will see the list of Damona commands (may be different with time) (may be::

    activate
    clean
    deactivate
    env
    export
    info
    install
    list
    remove
    search
    stats

To get help for the install command, type::

    damona install --help

Environments
------------

Damona provides a way to manage environments where Singularity images and binaries are installed.
Environments are independent from each other. We decided to go for a very simple design where an environment is nothing
else than a physical directory with a subdirectory called *bin/* to store the binaries. All images are shared between
environments to decrease the storage needs.

list environments
~~~~~~~~~~~~~~~~~~

If you type::

    damona env

You will get the list of environments available on your system. In theory, if you start from scratch there is only one
called **base** that cannot be deleted or created. You can use it as a sandbox though where software can be installed or removed.

Create environments
~~~~~~~~~~~~~~~~~~~

All environments are stored in ~/.config/damona/envs/. You can create a new one as follows::

    damona env --create TEST

There, you have a bin directory where binaries are going to be installed.

You can check that it has been created::

    damona env

Note the last line telling you that::

    Your current env is 'TEST'.

Activate/Deactivate environments
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
In order to install new binaries or software packages, you must activate an environment. You may activate several but the last one is the active one. Let us activate the TEST environment::

    damona activate TEST

Check that it is active using::

    damona env

and look at the last line. It should look like::

    Your current env is 'TEST'.


What is going on when you activate an environment called TEST ? Simple: we append the directory ~/.config/damona/envs/TEST/bin to your PATH where binaries are searched for. This directory is removed when you use the deactivate command.
::

    damona deactivate TEST
    damona env

should remove the TEST environment from your PATH. You may activate several and deactivate them. In such case, the environments behave as a Last In First Out principle::

    damona activate base
    damona activate TEST
    damona deactivate

Removes the last activated environments. While this set of commands is more specific::

    damona activate base
    damona activate TEST
    damona deactivate base

and keep the TEST environment only in your PATH.



Software and releases
---------------------

Search for existing software
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Damona** itself contains metadata to download containers and installed software. As explained in the motivation, other
projects provide thousands of containers but here we provide containers for
testing and proof of concept.

By default, **Damona** uses recipes, which can be found in the
https://github.com/damona/damona/recipes directory. In the registry files (see
later for details), we define the URL where images can be downloaded. Some are
on https://cloud.sylabs.io/library/cokelaer collection, which is limited to 10Gb
and therefore will not provide many containers. Others are on external registry
and one can define its own registry for its projects.

To get a list of the available containers in **Damona**, type::

   damona search "*" --images-only

You should see the container names and their version. You should also see where
the file is going to be downloaded from.

You can search for specific pattern using::

    damona search fastqc

This is not a lot indeed. So, we provide a system where you can look for
containers elsewhere on internet. For now, there is only one registry available
on https://biomics.pasteur.fr/salsa/damona (again for demonstration). There, we posted
some containers and a registry.txt file; if you type::

    damona search "*" --url https://biomics.pasteur.fr/salsa/damona/registry.txt

you will get a list of the images that are available. Anybody can provide a
container on any website with a registry.txt and you will be able to access to
the images.

The latter command can be simplified into ::

    damona search "*" --url damona

This is possible by defining alias in the configuration file (in
~/config/damona.cfg as explained in the developer guide)



Download and install an image
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The first thing to do before installing is software is to activate the environment where you wish to install the
software::

    damona env

tells you which is currently active. Otherwise activate one::

    damona activate TEST

See above for more details.

Given the container name and version, you can now download a container image as follows::

    damona install fastqc:0.11.9

If there are several version and you just want the latest, remove the tag::

    damona install fastqc

That's it, you should get the image in your config path ~/.config/damona/images
directory. In addition, a binary alias is created in ~/.config/damona/bin

And the *fastqc* command should be available::

    fastqc

.. note:: using the activate command above, your PATH has been changed in your current shell. If you open a new shell,
   you will need to activate the environment again.

To install an image/binary, you can also use an external registry (see developer
guide to define your own registry)::

    damona install fastqc:0.11.9 --url https://biomics.pasteur.fr/drylab/damona/registry.txt

For this particular website, we have an alias::

    damona install fastqc:0.11.9 --url damona

You can add aliases in *~/.config/damona/damona.cfg* file.

Application: set several Environments
--------------------------------------

In **damona**, environments are stored in *~/.config/damona*. There, you have two sub-directories:

* envs
* images

In the *images* directory, we store the singularity containers. In *envs* directory, we store the environments.
There, a sub-directory **bin/** can be found. That is where we create aliases
so as to make the container executables.

Now what about having different environments ? It would be nice to handle
several pipelines in their own environments.

We could quickly test two different versions of a tools and test their impact on an
analysis.::

    damona env --create test1
    damona env --create test2

Now, you need to activate the first one::

    damona activate test1

and install a tool with a given version in this environment::

    damona install fastqc:0.11.9

And to install it in the *test2* environment::

    damona deactivate
    damona activate test2
    damona install fastqc:0.11.8 --url damona

You can activate as many environments as you wish. Calling deactivate will only
deactivate the last activated environment. In works as a Last In First Out mechanism.


Install binaries not in the registry
-------------------------------------

When Damona's develope create a container, the also associate a list of binaries to be installed. This list is provided in a registry file (registry.yaml). 

For example, when installing the *fastqc* container, one binary called *fastqc* is created. Other containers may contain several binaries.

Note, however, that the list of binaries may not be complete. If so, users need to informa damona's developer, who have to change the registry, create a release, publish the release; then users have to be aware of that release, and update damona. This may be time consumming and is not dynamic enough.

If a user knows that a binary is present in a container, but not installed, he can sill install the binary as follows::

    damona install mummer --binaries show-snps




Environmental variables
------------------------
DAMONA_SINGULARITY_OPTIONS
~~~~~~~~~~~~~~~~~~~~~~~~~~

All binaries created with **Damona** use this syntax::

    singularity -s exec ${DAMONA_SINGULARITY_OPTIONS} ${DAMONA_PATH}/images/<IMAGE> <EXE> ${1+"$@"}

where EXE is the name of the executable binary, IMAGE the name of the container.
Then, you can see two environmental variables.

The DAMONA_SINGULARITY_OPTIONS can be used to provide any required options to singularity.
If undefined, it is set to an empty string. Otherwise, you can defined it as follows:

    export DAMONA_SINGULARITY_OPTIONS="whatever_you_need"

Note anout display and the -e option.

It is usually good practive to set the -e option to not use the environement where you start the container. However, you may have issue with X11 display. Indeed, -e means do not use any environment variable. Therefore the DISPLAY is unset. If such case, you can use::

    export DAMONA_SINGULARITY_OPTIONS=" -e --env DISPLAY=:1"


Example: Binding directories
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This variable is especially useful would you need to bind a path that is not present in
standard configuration. For example, on a cluster where your admin system set up
a local scratch in /local/scratch, you can tell singularity to look there by
binding this path into your container::

    export DAMONA_SINGULARITY_OPTIONS="-B /local/scratch:/local/scratch"
