Notes
-----

This is an environment rather than a recipe. It can be re-used by other recipes.

::

    Bootstrap: library
    From: cokelaer/damona/conda:4.7.12


4.7.12
------

This image starts from ubuntu 16.04 (xenial) and provide conda version 4.7.12

This includes libraries that allows to built pyqt correctly.
Fixes GTK warning and set conda channels fo R, bioconda, conda-forge

Python version is 3.6

Matplotlib backend it AGG

4.9.12
------

Updated with ubuntu 18.04
conda environment provides Python 3.7.3
