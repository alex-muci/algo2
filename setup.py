#!/usr/bin/python
# -*- coding: utf-8  -*-
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'My algo platform',
    'author': 'Alessandro Muci',
    'url': 'https://github.com/alex-muci/Algo2',
    'download_url': 'https://github.com/alex-muci/Algo2',
    'author_email': 'alex.muci@gmail.com',
    'version': '0.1',
    'install_requires': ['nose'],
    'packages': ['algo2'],
    'script': [],
    'name': 'algo2'
}

setup(**config)
