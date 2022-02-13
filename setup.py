#!/usr/bin/python
# -*- coding: utf-8 -*-
from dnsblock import const
import re

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

readme = open('README.rst', 'r').read()

requirements = []
with open('requirements.txt') as handle:
    for line in handle.readlines():
        if not line.startswith('#'):
            package = line.strip().split('=', 1)[0]
            requirements.append(package)

setup(
    name='dnsblock',
    version=const.__version__,
    description='dns blocklist automation and maintenance tools',
    author='Steven Wills',
    author_email='steven+dnsblock@swills.me',
    url='https://github.com/swills1/python-dnsblock.git',
    packages=['dnsblock'],
    license='BSD 3-Clause',
    install_requires=requirements,
    python_requires='>=3.10',
    long_description=readme,
    keywords=['dns', 'blocklist'],
    zip_safe=False,
    classifiers=[
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: BSD License',
    ]
)