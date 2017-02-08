#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import sys
import itertools
import os
from munch import munchify

PY2 = sys.version_info[0] == 2  # PY2 = sys.version_info.major == 2
# PY3 = (sys.version_info[0] >= 3)

################################################
# for serialisation, cPickle 100x faster than native
try:
    # noinspection PyPep8Naming
    import cPickle as pickle
except ImportError:
    import pickle

################################################
# folders for DATA and OUT(puts),
# defined in one place only for ease of future potential changes
def get_updir_wfld(folder_string):
    algo2_dir = os.path.dirname(os.path.dirname(__file__))  # parent dir of current one
    return os.path.join(algo2_dir, folder_string)  # ~/folder


DEFAULT = munchify({
    "CSV_DATA_DIR": get_updir_wfld("data"),
    "OUTPUT_DIR": get_updir_wfld("out")
})

################################################
# Python 2.7 vs. Python 3.x, compatibility
# source: utils.py3 in backtrader

if PY2:
    try:
        import _winreg as winreg
    except ImportError:
        winreg = None

    # noinspection PyPep8Naming
    import Queue as queue

    MAXINT = sys.maxint
    MININT = -sys.maxint - 1

    MAXFLOAT = sys.float_info.max
    MINFLOAT = sys.float_info.min

    string_types = str, unicode
    integer_types = int, long

    filter = itertools.ifilter
    map = itertools.imap
    range = xrange
    zip = itertools.izip
    long = long

    cmp = cmp

    bytes = bytes
    bstr = bytes

#    from io import StringIO

#    from urllib2 import urlopen
#    from urllib import quote as urlquote

    # noinspection PyCompatibility
    def iterkeys(d):
        return d.iterkeys()

    # noinspection PyCompatibility
    def itervalues(d):
        return d.itervalues()

    # noinspection PyCompatibility
    def iteritems(d):
        return d.iteritems()

    def keys(d):
        return d.keys()

    def values(d):
        return d.values()

    def items(d):
        return d.items()

else:
    try:
        import winreg
    except ImportError:
        winreg = None

    import queue as queue

    MAXINT = sys.maxsize
    MININT = -sys.maxsize - 1

    MAXFLOAT = sys.float_info.max
    MINFLOAT = sys.float_info.min

    string_types = str,
    integer_types = int,

    filter = filter
    map = map
    range = range
    zip = zip
    long = int

    def cmp(a, b):
        return (a > b) - (a < b)

    def bytes(x):
        return x.encode('utf-8')

    def bstr(x):
        return str(x)

#    from io import StringIO

#    from urllib.request import urlopen
#    from urllib.parse import quote as urlquote

    def iterkeys(d):
        return iter(d.keys())

    def itervalues(d):
        return iter(d.values())

    def iteritems(d):
        return iter(d.items())

    def keys(d):
        return list(d.keys())

    def values(d):
        return list(d.values())

    def items(d):
        return list(d.items())
