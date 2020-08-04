Overview
############

First, you should get the list of existing containers::

   damona list 

you can filter by selecting a specific pattern::

    damona list --pattern qc


Then, you can download the image::

    damona pull fastqc

That's it, you should get the image in your config path ~/.config/damona/images

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

