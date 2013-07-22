#! /usr/bin/env python
import sys
import os
import screed

filename = sys.argv[1]

try:
    os.unlink(filename + '_screed')
except OSError:
    pass

db = screed.read_fasta_sequences(filename)

###

from whoosh.index import create_in
from whoosh.fields import *
schema = Schema(name=TEXT(stored=True),
                description=TEXT(stored=True))

import os, shutil
indexdir = filename + '.whooshd'
try:
    shutil.rmtree(indexdir)
except OSError:                 # doesn't exit
    pass

os.mkdir(indexdir)
ix = create_in(indexdir, schema)

writer = ix.writer()
for r in db.itervalues():
    writer.add_document(name=unicode(r.name),
                        description=unicode(r.description))

writer.commit()

