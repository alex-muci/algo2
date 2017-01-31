# TODO get some more compat from BACKTRADER

import sys

PY2 = sys.version_info[0] == 2
PY3 = (sys.version_info[0] >= 3)

if PY2:
    import Queue as queue
else:
    import queue

# for serialisation, cPickle 100x faster
try:
    import cPickle as pickle
except ImportError:
    import pickle
