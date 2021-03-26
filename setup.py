# -*- encoding: utf-8 -*-

from pathlib import Path

from setuptools import find_packages
from setuptools import setup

setup(
    name='homeproc',
    version='0.0.1',
    author='Paul Iacomi',
    author_email='mail@pauliacomi.com',
    py_modules=['homeproc'],
    python_requires='>=3.6',
    setup_requires=[
        'setuptools_scm',
        'pytest-runner',
    ],
    install_requires=[
        'numpy',
        'scipy',
        'pandas',
        'matplotlib',
    ],
)
