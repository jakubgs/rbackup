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
    url='https://github.com/PonderingGrower/rbackup',

    python_requires='>=3.5',

    test_suite='test',
    tests_require=['pytest'],

    entry_points={
        'console_scripts': [
            'rbackup = rbackup.script:main'
        ],
    },

    # dependencies
    install_requires=[
        'sh',
        'pyyaml',
    ],
    setup_requires=[
        'mock',
        'pytest',
        'pytest_cov',
    ]
)
