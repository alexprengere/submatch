#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division

import os, sys
import os.path as op
from itertools import product
from contextlib import contextmanager
from StringIO import StringIO
from functools import wraps

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
def comments(comment_char='#'):
    """Add comments to print statement.
    """
    # Replacing stdout by a local StringIO
    sys.stdout = s = StringIO()
    yield
    sys.stdout = sys.__stdout__

    for line in s.getvalue().rstrip().split('\n'):
        print comment_char, line
    s.close()


def cached(func):
    """Cache decorator for a function with no keywork argument.
    """
    cache = {}

    @wraps(func)
    def new_func(*args):
        # Simple case here
        key = args
        if key not in cache:
            cache[key] = func(*args)
        return cache[key]

    return new_func


def files_with_ext(*extensions):
    """List all files having an extension.

    >>> list(files_with_ext('avi'))
    ['movie.avi', 'movie_2.avi']
    """
    authorized_extensions = set(extensions) # faster lookup

    for root, _, files in os.walk('.', topdown=False):
        for name in files:
            # Extension without leading '.'
            # Made non case sensitive
            ext = op.splitext(name)[1][1:].lower()

            if ext in authorized_extensions:
                yield op.join(root, name)


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
        ratio = distance_names(sub, movie)
        print '{0:.0f}%\t{1}\t->\t{2}'.format(100 * ratio, movie, sub)

    if remaining_subs:
        print '* Remaining subs  :', ' '.join(remaining_subs)

    if remaining_movies:
        print '* Remaining movies:', ' '.join(remaining_movies)


@cached
def distance_names(a, b):
    """Compare names without extensions.
    """
    a = op.splitext(op.basename(a))[0]
    b = op.splitext(op.basename(b))[0]

    return ratio(a.lower(), b.lower())


def match(movies, subtitles, limit, reverse):
    """Match movies and subtitles.
    """
    # Store the mapping movie -> sub
    mapping = OrderedDict()
    attributed_subs = set()

    # Finding best sub for this movie
    pairs = sorted(product(movies, subtitles),
                   key=lambda p: distance_names(*p),
                   reverse=True)

    for movie, sub in pairs:
        # Check if movie/sub has already been used
        if movie in mapping or sub in attributed_subs:
            continue

        # Then, if ratio is too bad we end the attribution process
        if distance_names(movie, sub) < limit:
            break

        # We do not want this sub/movie to be used again
        mapping[movie] = sub
        attributed_subs.add(sub)

    # Now we print the bash script
    print '#!/bin/bash\n'

    if not mapping:
        print 'echo No mapping! Check if movies/subs'
        return

    with comments():
        remaining_movies = set(movies) - set(mapping)
        remaining_subs = set(subtitles) - attributed_subs

        print_report(mapping,
                     remaining_movies=remaining_movies,
                     remaining_subs=remaining_subs)

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
        metavar='L',
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
        movies.extend(sorted(files_with_ext('')))

    match(movies,
          subtitles,
          limit=args.limit,
          reverse=args.reverse)


if __name__ == '__main__':

    main()
