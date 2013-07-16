#! /usr/bin/env python
import sys
import pygr.seqdb
import os

filename = sys.argv[1]

try:
    os.unlink(filename + '.pureseq')
except OSError:
    pass

try:
    os.unlink(filename + '.seqlen')
except OSError:
    pass
    
pygr.seqdb.BlastDB(filename)
