from https://dnascent.readthedocs.io/en/latest/installation.html documentation July 2023.

In new versions of MinKNOW, the fast5 files are compressed with VBZ Compression (see https://github.com/nanoporetech/vbz_compression). To use these compressed fast5 files,

Go to https://github.com/nanoporetech/vbz_compression/releases and download the plugin appropriate for your processor architecture. In this example, we’ll use ont-vbz-hdf-plugin-1.0.1-Linux-x86_64.tar.gz.

Download and unpack the plugin::

    wget https://github.com/nanoporetech/vbz_compression/releases/download/v1.0.1/ont-vbz-hdf-plugin-1.0.1-Linux-x86_64.tar.gz
    tar -xf ont-vbz-hdf-plugin-1.0.1-Linux-x86_64.tar.gz

Add the plugin to your path::

    export HDF5_PLUGIN_PATH=/full/path/to/ont-vbz-hdf-plugin-1.0.1-Linux/usr/local/hdf5/lib/plugin
