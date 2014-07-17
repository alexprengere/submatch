#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division

import sys
import os.path as op
from glob import glob
from itertools import product
from contextlib import contextmanager
from StringIO import StringIO

# Installed through setup.py
from Levenshtein import ratio
from ordereddict import OrderedDict

# Extension used
EXT_MOVIE = 'avi', 'mkv', 'mp4', \
            'flv', 'wmv', '3gp', \
            'mov'

EXT_SUBTITLE = 'srt', 'sub', 'smi'

# Minimal matching ratio
DEFAULT_RATIO = 0.60


@contextmanager
def comments(char='#'):
    """Add comments to print statement.
    """
    sys.stdout = s = StringIO()
    yield
    sys.stdout = sys.__stdout__
    for line in s.getvalue().split('\n'):
        print char, line.rstrip()
    s.close()


def files_with_ext(*extensions):
    """List all files having an extension.

    >>> list(files_with_ext('avi'))
    ['movie.avi', 'movie_2.avi']
    """
    for ext in extensions:
        for filename in glob('*.{0}'.format(ext.lower())):
            yield filename
        for filename in glob('*.{0}'.format(ext.upper())):
            yield filename


def print_mv(mapping, reverse):
    """Print the final bash script.
    """
    print
    for movie, sub in mapping.iteritems():
        if reverse:
            # Build new name for sub
            new_sub = op.splitext(movie)[0] + op.splitext(sub)[1]
            if sub != new_sub:
                print 'mv {0} {1}'.format(sub, new_sub)
            else:
                print '# {0} has the right name ;)'.format(sub)

        else:
            # Build new name for movie: sub name + original movie extension
            new_movie = op.splitext(sub)[0] + op.splitext(movie)[1]
            if movie != new_movie:
                print 'mv {0} {1}'.format(movie, new_movie)
            else:
                print '# {0} has the right name ;)'.format(movie)


def print_report(mapping, remaining_movies, remaining_subs):
    """Report is displayed commented.
    """
    print '* Mapping:'

    for movie, sub in mapping.iteritems():
        ratio = compare_names(sub, movie)
        print '{0:.0f}%\t{1}\t->\t{2}'.format(100 * ratio, movie, sub)

    if remaining_subs:
        print '* Remaining subs  :', ' '.join(remaining_subs)

    if remaining_movies:
        print '* Remaining movies:', ' '.join(remaining_movies)


def compare_names(a, b):
    """Compare names without extensions.
    """
    a = op.splitext(op.basename(a))[0]
    b = op.splitext(op.basename(b))[0]

    return ratio(a.lower(), b.lower())


def match(movies, subtitles, limit, reverse):
    """Match movies and subtitles.
    """
    # We copy, this will be modify along attribution to movies
    available_movies = movies[:]
    available_subs = subtitles[:]

    # Store the mapping movie -> sub
    mapping = OrderedDict()

    while True:
        # Perhaps all subtitles have already been attributed
        if not available_subs or not available_movies:
            break

        # Finding best sub for this movie
        # Then, if ratio is too bad we skip
        best_pair = max(product(available_movies, available_subs),
                        key=lambda p: compare_names(*p))

        best_ratio = compare_names(*best_pair)
        if best_ratio < limit:
            break

        # Storing result in mapping, and removing from available
        # We do not want this sub/movie to be used again
        movie, sub = best_pair

        mapping[movie] = sub
        available_movies.remove(movie)
        available_subs.remove(sub)

    # Now we print the bash script
    print '#!/bin/bash\n'

    if not mapping:
        print 'echo No mapping! Check if movies/subs'
        return

    with comments():
        print_report(mapping,
                     remaining_movies=available_movies,
                     remaining_subs=available_subs)

    print_mv(mapping, reverse=reverse)


def main():
    """Main runner.
    """
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-l', '--limit',
        type=float,
        default=DEFAULT_RATIO,
        help="""
        Change lower bound for matching ratio.
        Default is %(default)s. Matches below
        that percentage are automatically excluded.
        """)

    parser.add_argument(
        '-r', '--reverse',
        action='store_true',
        help="""
        Reverse the logic of renaming.
        With this option, subtitles are
        renamed, not movies.
        """)

    parser.add_argument(
        '-n', '--no-ext',
        action='store_true',
        help="""
        Consider files with no extension as movies.
        """)

    args = parser.parse_args()

    movies = sorted(files_with_ext(*EXT_MOVIE))
    subtitles = sorted(files_with_ext(*EXT_SUBTITLE))

    if args.no_ext:
        movies.extend([f for f in glob('*') if not op.splitext(f)[1]])

    match(movies,
          subtitles,
          limit=args.limit,
          reverse=args.reverse)


if __name__ == '__main__':

    main()
