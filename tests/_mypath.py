import sys, os

thisdir = os.path.abspath(os.path.dirname(__file__))
libdir = os.path.join(thisdir, '../lib/')
libdir = os.path.abspath(libdir)

if libdir not in sys.path:
    sys.path.insert(0, libdir)
