#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import with_statement

import os.path as op
from setuptools import setup


def local(rel_path, root_file=__file__):
    return op.join(op.realpath(op.dirname(root_file)), rel_path)


with open(local('VERSION')) as fl:
    VERSION = fl.read().rstrip()

with open(local('README.rst')) as fl:
    LONG_DESCRIPTION = fl.read()

with open(local('LICENSE')) as fl:
    LICENSE = fl.read()

setup(
    name='submatch',
    version=VERSION,
    author='Alex Prengère',
    author_email='alexprengere@gmail.com',
    url='https://github.com/alexprengere/submatch',
    description='Match movies and subtitles from their names.',
    long_description=LONG_DESCRIPTION,
    license=LICENSE,
    #
    # Manage standalone scripts
    entry_points={
        'console_scripts': [
            'submatch = sub_match:main'
        ]
    },
    py_modules=[
        'sub_match'
    ],
    install_requires=[
        'python_Levenshtein',
    ],
)
