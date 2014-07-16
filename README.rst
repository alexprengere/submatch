submatch
========

This is a Python utility to match movies and subtitles inside a directory,
based on their names. It is specially useful for series with lots of subtitles.
It will test all possibilities of matching with one subtitle per movie, and keep
the best global matching.

Installation
------------

.. code-block:: bash

 $ python setup.py install --user

Example
-------

.. code-block:: bash

 $ cd example
 $ ls
 tata.avi  toto.avi  toto.srt  tutu.avi  tutu.fr.srt

 $ submatch > result.sh
 ## Mapping #0 (86%):
 tutu.avi   ->  tutu.fr.srt 73%
 toto.avi   ->  toto.srt    100%

 # Remaining movies:
 tata.avi

 $ cat result.sh
 #!/bin/bash
 mv tutu.avi tutu.fr.avi
 mv toto.avi toto.avi
