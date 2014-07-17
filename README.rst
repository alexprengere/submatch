submatch
========

This is a Python utility to match movies and subtitles inside a directory,
based on their names. It is specially useful for series with lots of subtitles.
It will test different possibilities of matching with one subtitle per movie, and keep
the best global matching.

The output is a shell script containing the right ``mv`` commands.

Installation
------------

.. code-block:: bash

 $ python setup.py install --user

Usage
-----

.. code-block:: bash

 $ submatch -h
 usage: sub_match.py [-h] [-l LIMIT] [-r] [-v]
 
 optional arguments:
   -h, --help            show this help message and exit
   -l LIMIT, --limit LIMIT
                         Change lower bound for matching ratio. Default is 0.2.
                         Matches below that percentage are automatically
                         excluded.
   -r, --reverse         Reverse the logic of renaming. With this option,
                         subtitles are renamed, not movies.
   -v, --verbose         Display information for each matching test.

Example
-------

.. code-block:: bash

 $ touch tata.avi toto.avi toto.srt tutu.avi tutu.fr.srt

 $ submatch
 #!/bin/bash
 
 # * Mapping #best (average 86%):
 # 73%	tutu.avi	->	tutu.fr.srt
 # 100%	toto.avi	->	toto.srt
 # * Remaining movies: tata.avi
 
 mv tutu.avi tutu.fr.avi

 $ submatch | sh
