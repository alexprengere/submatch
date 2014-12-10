#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division

import os, sys
import os.path as op
from itertools import product
from contextlib import contextmanager
from StringIO import StringIO
from functools import wraps
from textwrap import dedent
import re

# Installed through setup.py
import Levenshtein
from ordereddict import OrderedDict
import colorama
from termcolor import colored

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


COLORS = [
    ('white', 'on_grey'),
    ('white', 'on_red'),
    ('white', 'on_green'),
    ('white', 'on_yellow'),
    ('white', 'on_blue'),
    ('white', 'on_magenta'),
    ('white', 'on_cyan'),
    ('grey', 'on_white'),
]

def extract_numbers(name):
    """Extract numbers from string."""
    name = op.splitext(op.basename(name))[0]
    return [int(d) for d in re.findall(r'\d+', name)]


def compute_colors(number):
    """Compute color based on number."""
    return COLORS[number % len(COLORS)]


def fmt(name):
    numbers = extract_numbers(name)
    colors = compute_colors(sum(numbers) if numbers else 0)

    flat_numbers = '/'.join(str(d) for d in numbers)
    return colored('[{0:<6s}] {1:60s}'.format(flat_numbers, name), *colors)


def fmt_ratio(ratio):
    if ratio == 100:
        colors = ('white', 'on_green')
    elif ratio >= 90:
        colors = ('grey', 'on_white')
    elif ratio >= 80:
        colors = ('white', 'on_yellow')
    elif ratio >= 70:
        colors = ('white', 'on_red')
    else:
        colors = ('white', 'on_magenta')

    return colored('{0:5.1f}%'.format(ratio), *colors)


def print_report(method, mapping, remaining_movies, remaining_subs):
    """Report is displayed commented.
    """
    if remaining_subs:
        print '\nUnmatched subtitles:'
        print '\n'.join(fmt(r) for r in remaining_subs)

    if remaining_movies:
        print '\nUnmatched movies:'
        print '\n'.join(fmt(r) for r in remaining_movies)

    if not mapping:
        return

    print dedent("""
    Matching results with method "{0}":
     * column 1  : Levenshtein distance between movie name and sub name
     * column 2  : '✓' if movie name and sub name contain then same numbers
     * column 3+ : [numbers] movie ... [numbers] sub (color based on numbers)
    """.format(method.upper()))

    for movie, sub in mapping.iteritems():
        ratio = 100 * distance_of_names(sub, movie)
        mark = '✓' if extract_numbers(movie) == extract_numbers(sub) else ' '

        print '{0} {1} {2}{3}'.format(fmt_ratio(ratio), mark, fmt(movie), fmt(sub))


def move_to_match(name, ref):
    """Move name to match ref, but keep extension.
    """
    new_name = op.splitext(ref)[0] + op.splitext(name)[1]

    q = '"{0}"'.format
    if name != new_name:
        print 'mv {0:50s} {1:50s}'.format(q(name), q(new_name))
    else:
        print '# Already good: {0}'.format(q(new_name))


def print_moves(mapping, reverse):
    """Print the final bash script.
    """
    if not mapping:
        print '\necho >&2 "No mapping! Check match limit (-l) or try -z/-n"'
        return

    print '\n# Actual moves proposed'
    for movie, sub in mapping.iteritems():
        if reverse:
            move_to_match(movie, ref=sub)
        else:
            move_to_match(sub, ref=movie)


@cached
def distance_of_names(a, b):
    """Compare names without extensions.
    """
    a = op.splitext(op.basename(a))[0]
    b = op.splitext(op.basename(b))[0]

    return Levenshtein.ratio(a.lower(), b.lower())


@cached
def distance_of_numbers(a, b):
    """Compare number sequence.
    """
    a_numbers = extract_numbers(a)
    b_numbers = extract_numbers(b)

    if a_numbers and b_numbers and a_numbers == b_numbers:
        return 1
    return 0


def match(movies, subtitles, limit, method):
    """Match movies and subtitles.
    """
    if method == 'zip':
        # movies and subtitles are already sorted
        return OrderedDict(zip(movies, subtitles))

    if method == 'names':
        distance = distance_of_names
    elif method == 'numbers':
        distance = distance_of_numbers
    else:
        raise ValueError('Unkwown method {0}'.format(method))

    # Finding best sub for this movie
    pairs = sorted(product(movies, subtitles),
                   key=lambda p: distance(*p),
                   reverse=True)

    # Store the mapping movie -> sub
    mapping = OrderedDict()
    attributed_subs = set()

    for movie, sub in pairs:
        # Check if movie/sub has already been used
        if movie in mapping or sub in attributed_subs:
            continue

        # Then, if ratio is too bad we end the attribution process
        if distance(movie, sub) < limit:
            break

        # We do not want this sub/movie to be used again
        mapping[movie] = sub
        attributed_subs.add(sub)

    return mapping



def main():
    """Main runner.
    """
    colorama.init()

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
        With this option, movies are
        renamed, not subtitles.
        """)

    parser.add_argument(
        '-z', '--zip',
        action='store_true',
        help="""
        Change the logic of matching. Zip the sorted
        list of movies and subtitles instead of match
        on names. This will not use -l/--limit option.
        """)

    parser.add_argument(
        '-n', '--numbers',
        action='store_true',
        help="""
        Change the logic of matching. Use numbers in
        names to perform the matching.
        This will not use -l/--limit option.
        """)

    parser.add_argument(
        '-N', '--no-ext',
        action='store_true',
        help="""
        Consider files with no extension as movies.
        """)

    args = parser.parse_args()

    subtitles = sorted(files_with_ext(*EXT_SUBTITLE))
    movies = sorted(files_with_ext(*EXT_MOVIE))
    if args.no_ext:
        movies.extend(sorted(files_with_ext('')))

    if not movies and not subtitles:
        print 'echo >&2 "No movies/subs found! Move in the right folder!"'
        return

    if args.zip:
        method = 'zip'
    elif args.numbers:
        method = 'numbers'
    else:
        method = 'names'

    mapping = match(movies, subtitles, limit=args.limit, method=method)

    # Now we print the bash script
    with comments():
        remaining_movies = set(movies) - set(mapping)
        remaining_subs = set(subtitles) - set(mapping.itervalues())

        print_report(method,
                     mapping,
                     remaining_movies=remaining_movies,
                     remaining_subs=remaining_subs)

    print_moves(mapping, reverse=args.reverse)


if __name__ == '__main__':
    main()

