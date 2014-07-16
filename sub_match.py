#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
import os.path as op
from glob import glob
from itertools import permutations

# Installed through setup.py
from Levenshtein import ratio

# Extension used
EXT_MOVIE = 'avi', 'mkv', 'mp4'
EXT_SUBTITLE = 'srt', 'sub'

DEFAULT_RATIO = 0.20


def files_with_ext(*extensions):
    """List all files having an extension.

    >>> list(files_with_ext('avi'))
    ['movie.avi', 'movie_2.avi']
    """
    for ext in extensions:
        for filename in glob('*.{}'.format(ext)):
            yield filename


def print_mv(mapping, reverse):
    """Print the final bash script.
    """
    print
    for movie_name, best_sub in mapping.iteritems():
        if reverse:
            # Build new name for sub
            new_sub_name = op.splitext(movie_name)[0] + \
                           op.splitext(best_sub)[1]

            if best_sub != new_sub_name:
                print 'mv {0} {1}'.format(best_sub, new_sub_name)

        else:
            # Build new name for movie: sub name + original movie extension
            new_movie_name = op.splitext(best_sub)[0] + \
                             op.splitext(movie_name)[1]

            if movie_name != new_movie_name:
                print 'mv {0} {1}'.format(movie_name, new_movie_name)


def print_report(mapping, remaining_movies, remaining_subs, score=0, n=0):
    """Report is displayed commented.
    """
    print
    if not mapping:
        print '# No mapping! (check if movies/subs)'
    else:
        print '# * Mapping #{0} (average {1:.0f}%):'.format(n, 100 * score / len(mapping))

        for movie_name, sub in mapping.iteritems():
            ratio = compare_names(sub, movie_name)
            print '# {0:.0f}%\t{1}\t->\t{2}'.format(100 * ratio, movie_name, sub)

    if remaining_subs:
        print '# * Remaining subs  :', ' '.join(remaining_subs)

    if remaining_movies:
        print '# * Remaining movies:', ' '.join(remaining_movies)


def compare_names(a, b):
    """Compare names without extensions.
    """
    a = op.splitext(op.basename(a))[0]
    b = op.splitext(op.basename(b))[0]

    return ratio(a, b)


def match(movies, subtitles, limit, reverse, verbose):
    """Match movies and subtitles.
    """
    print '#!/bin/bash'

    # We want to optimize the global score of matching, so we
    # test all order of files as input
    best_mapping = {}
    best_score = 0

    for n, movie_list in enumerate(permutations(movies)):
        # Store the mapping movie -> sub
        # We copy subtitles, this will be modify along attribution to movies
        mapping = {}
        available_subs = subtitles[:]
        score = 0

        for movie_name in movie_list:
            # Perhaps all subtitles have already been attributed
            if not available_subs:
                break

            # Finding best sub for this movie
            # Then, if ratio is too bad we skip
            best_sub = max(available_subs, key=lambda s: compare_names(s, movie_name))

            best_ratio = compare_names(best_sub, movie_name)
            if best_ratio < limit:
                continue

            # Storing result in mapping, and removing sub from available_subs
            # We do not want this sub to be used again
            mapping[movie_name] = best_sub
            available_subs.remove(best_sub)
            score += best_ratio

        if score > best_score:
            best_score = score
            best_mapping = mapping

        if verbose:
            print_report(mapping,
                         remaining_movies=[m for m in movies if m not in mapping],
                         remaining_subs=[s for s in subtitles if s not in mapping.values()],
                         score=score, n=n)

    print_report(best_mapping,
                 remaining_movies=[m for m in movies if m not in best_mapping],
                 remaining_subs=[s for s in subtitles if s not in best_mapping.values()],
                 score=best_score)

    if mapping:
        print_mv(best_mapping, reverse)


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
        '-v', '--verbose',
        action='store_true',
        help="""
        Display information for each matching test.
        """)

    args = parser.parse_args()

    movies = sorted(files_with_ext(*EXT_MOVIE))
    subtitles = sorted(files_with_ext(*EXT_SUBTITLE))

    match(movies, subtitles, args.limit, args.reverse, verbose=args.verbose)


if __name__ == '__main__':

    main()
