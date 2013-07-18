#! /usr/bin/env python
import sys
import os
import screed

filename = sys.argv[1]

try:
    os.unlink(filename + '_screed'
except OSError:
    pass

screed.read_fasta_sequences(filename)
