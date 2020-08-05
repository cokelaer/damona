Usage
############

List available images to be downloaded
--------------------------------------

First, you should get the list of existing containers::

   damona list 

you can filter by selecting a specific pattern::

    damona list --pattern qc

Download an image
-----------------

You can download an image given its full name and tag::

    damona pull fastqc:0.11.9

If there are several version and you just want the latest::

    damona pull fastqc

That's it, you should get the image in your config path ~/.config/damona/images
directory.

There is a registry-like system: a registry.yaml file stores the name of the
image and the executables that is (are) provided. Here, a fastqc executale is
available within the images. However, this requires to call it in a specific
mannaer::

    singularity run name.img fastqc


Instead, we set a binary in ~/.config/damona/bin/fastqc that does this for you. 

All you need to do is call the executable from this directory. Even better, set
your environment to look for executablers in ~/.config/damona/bin/ For example::

    export PATH=~/.config/damona/bin/:$PATH

and you are ready do go.


Build an image from yours
-------------------------
This command builds a recipe and save the image in **recipes.img file**
whereever is the Singularity.recipes file::

    damona build Singularity.recipes

You can save the image elsewhere::

    damona build Singularity.recipes --output-name ~/temp.img

This is nothing more than an alias to singularity itself::

     singularity build recipes Singularity.recipes

More interesting is the ability to build a local version of a recipes to be
found in damona::

    damona build salmon:1.3.0

this will find the recipes automatically and save the final container in
**salmon_1.3.0.img**.

Setup an environment
--------------------






