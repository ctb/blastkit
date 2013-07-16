import blastkit

BASEDIR='/home/t/blastkit/bk.dev/'

blastkit.BLAST = '/usr/bin/blastall'
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
