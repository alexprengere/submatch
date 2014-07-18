SubMatch
========

This is a Python utility to match movies and subtitles inside a directory,
based on their names. It is specially useful for series with lots of subtitles.

The output is a shell script containing the right ``mv`` commands.

Installation
------------

.. code-block:: bash

 $ python setup.py install --user

Usage
-----

.. code-block:: bash

 $ submatch -h
 usage: sub_match.py [-h] [-l L] [-r] [-n]
 
 optional arguments:
   -h, --help       show this help message and exit
   -l L, --limit L  Change lower bound for matching ratio. Default is 0.6.
                    Matches below that percentage are automatically excluded.
   -r, --reverse    Reverse the logic of renaming. With this option, movies are
                    renamed, not subtitles.
   -n, --no-ext     Consider files with no extension as movies.

Example
-------

Suppose you have some movies and subtitles:

.. code-block:: bash

 $ touch tata.avi titi.sub toto.avi toto.srt TUTU.AVI tutu.fr.srt

After installation, just run the tool in the folder:

.. code-block:: bash

 $ submatch
 # * Mapping:
 # 100%	./toto.avi	->	./toto.srt
 # 73%	./TUTU.AVI	->	./tutu.fr.srt
 # * Remaining subs  : ./titi.sub
 # * Remaining movies: ./tata.avi
 
 # ./toto.srt has the right name ;)
 mv ./tutu.fr.srt ./TUTU.srt

You can then actually perform the move like this:

.. code-block:: bash

 $ submatch | sh
