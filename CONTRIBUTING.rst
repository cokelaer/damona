================================
Damona contributing guidelines
================================

Main development
================

If you are interesting in helping on the core development, just create an issue to enter in contact, or create pull requests.

Recipes
========

If you have a Singularity recipes and wish to add it, simply create a directory named after the tool (small caps) in ./damona/recipes and add the Singularity recipe. It should be named::

    Singularity.name_x.y.z
    
x,y,z being the version and **name** the name of the tool (small caps as much as possible; )    

Issues
==========

You have an issue ? You found a bug ? Please submit an issue with 

- a description of the problem
- the version of Damona used
- the error message if any


pull requests
===================

Pull requests are always welcome, and the Damona community appreciates
any help you give.

When submitting a pull request, we ask you to check the following:

1. **Unit tests**, **documentation**, and **code style** are in order. 
   
   It's also OK to submit work in progress if you're unsure of what
   this exactly means, in which case you'll likely be asked to make
   some further changes.

2. The contributed code will be **licensed under Damona's license**,
   https://github.com/cokelaer/damona/blob/master/LICENSE
   If you did not write the code yourself, you ensure the existing
   license is compatible and include the license information in the
   contributed files, or obtain a permission from the original
   author to relicense the contributed code.
