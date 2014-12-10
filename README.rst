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
 usage: submatch [-h] [-l L] [-r] [-z] [-n] [-N]
 
 optional arguments:
   -h, --help       show this help message and exit
   -l L, --limit L  Change lower bound for matching ratio. Default is 0.6.
                    Matches below that percentage are automatically excluded.
   -r, --reverse    Reverse the logic of renaming. With this option, movies are
                    renamed, not subtitles.
   -z, --zip        Change the logic of matching. Zip the sorted list of movies
                    and subtitles instead of match on names. This will not use
                    -l/--limit option.
   -n, --numbers    Change the logic of matching. Use numbers in names to
                    perform the matching. This will not use -l/--limit option.
   -N, --no-ext     Consider files with no extension as movies.

Example
-------

Suppose you have some movies and subtitles:

.. code-block:: bash

 $ touch tata.avi titi.sub toto.avi toto.srt TUTU.AVI tutu.fr.srt

After installation, just run the tool in the folder:

.. code-block:: bash

 $ submatch
 # 
 # Unmatched subtitles:
 # [      ] ./titi.sub                                                  
 # 
 # Unmatched movies:
 # [      ] ./tata.avi                                                  
 # 
 # Matching results with method "NAMES":
 #  * column 1  : Levenshtein distance between movie name and sub name
 #  * column 2  : '✓' if movie name and sub name contain then same numbers
 #  * column 3+ : [numbers] movie ... [numbers] sub (color based on numbers)
 # 
 # 100.0% ✓ [      ] ./toto.avi              [      ] ./toto.srt
 #  72.7% ✓ [      ] ./TUTU.AVI              [      ] ./tutu.fr.srt
 
 # Actual moves proposed
 # Already good: "./toto.srt"
 mv "./tutu.fr.srt" "./TUTU.srt" 

You can then actually perform the move like this:

.. code-block:: bash

 $ submatch | sh

