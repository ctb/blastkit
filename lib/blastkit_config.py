import blastkit
import os.path

BASEDIR='/root/blastkit/'
def _basedir(x):
    return os.path.join(BASEDIR, x)

blastkit.BLAST = '/usr/local/bin/blastall'
blastkit.tempdir = BASEDIR + 'www/files'
blastkit.dbs = BASEDIR + 'db/'

databases = [
    dict(id='test-dna', filename=blastkit.dbs + 'test-dna.fa',
         name='Test database',
         seqtype='DNA'),
    dict(id='test-prot', filename=blastkit.dbs + 'test-prot.fa',
         name='Test database',
         seqtype='protein')
]
