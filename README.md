dupinator
=========

This is the original dupinator.py script created by Bill Bumgarner.

It can be found and discussed here:

- http://code.activestate.com/recipes/362459/

The script is used to find duplicate files, taking care to use as little CPU as possible, thus only comparing files of the same size, then checking the first kb for differences, and after that creating a checksum of the whole file.

