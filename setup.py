#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='rbackup',
    version='0.1',
    packages=find_packages(),

    author='Some Dude',
    author_email='i@always.fail',
    description='Utility for automating backups with tar & rsync.',
    license='PSF',
    keywords='backup rsync tar tarball automating',

    test_suite='test',

    entry_points={
        'console_scripts': [
            'rbackup = rbackup.script:main'
        ],
    },

    # dependencies
    install_requires=[
        'sh>=1',
    ],
    setup_requires=[
        'pytest>=2'
    ]
)
