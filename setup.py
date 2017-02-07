#!/usr/bin/python
# -*- coding: utf-8  -*-
try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup
	
config = {
	'description': 'My first Algo',
	'author':	'Alessandro Muci',
	'url':	'URL where to get it',
	'download_url':	'where to download it',
	'author_email':	'alex.muci@gmail.com',
	'version': '0.1',
	'install_requires': ['nose'],
	'packages': ['algo2'],
	'script': [],
	'name':	'projectname'
}

setup(**config)

