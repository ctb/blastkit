#! /u/t/dev/venv/bin/python
import sys
import shutil
import cPickle
import traceback
import os, os.path
import time

import _mypath
import blastkit
import blastparser
from pygr import seqdb

import cgi

###

PLACEHOLDER_MESSAGE = '''
<head><META http-equiv="refresh" content="5;"></head>
<body>
We're doing the BLAST!
<p>
<b>Don't hit reload!</b>
This page will automatically reload, and the results will be available here.
<p>
Results can take a few minutes.
</body>
'''

###

def do_cgi():
    """
    Main CGI function.  Retrieve form information, set up task, return
    placeholder, and spawn worker process.
    """
    
    # retrieve sequence from submitted form info
    form = cgi.FieldStorage()
    name = form['name'].value
    if not name.strip():
        name = 'query'

    seqtype = form['input'].value
    sequence = form['sequence'].value

    # make a working directory to save stuff in
    tempdir, dirstub = blastkit.make_dir()

    # write out the query sequence
    fp = open('%s/query.fa' % (tempdir,), 'w')
    if sequence.strip().startswith('>'):
        fp.write(sequence)
    else:
        fp.write('>%s\n%s\n' % (name, sequence,))
    fp.close()

    # write out the placeholder message
    fp = open('%s/index.html' % (tempdir,), 'w')
    fp.write(PLACEHOLDER_MESSAGE)
    fp.close()

    # fork response function / worker function
    blastkit.split_execution(response_fn, (dirstub,),
                             worker_fn, (seqtype, tempdir,))

def response_fn(dirstub):
    """
    Construct a new location & go there.
    """
    name = os.environ['SERVER_NAME']
    port = os.environ['SERVER_PORT']
    path = os.path.dirname(os.environ['SCRIPT_NAME'])
    
    url = 'http://%s:%s%s/files/%s' % (name, port, path, dirstub)

    time.sleep(1)
    
    print 'Location: %s\n' % (url,)

@blastkit.write_tracebacks_to_file
def worker_fn(seqtype, tempdir):
    """
    Run the BLAST and display the results.
    """
    dbfile = '/scratch/titus/mssm/pm-abund.k31.200.num.fa'
    newfile = tempdir + '/' + 'query.fa'

    if seqtype == 'protein':
        program = 'tblastn'
    else:
        program = 'blastn'
        
    out, err = blastkit.run_blast(program, newfile, dbfile, args=['-e 1e-6'])

    fp = open(tempdir + '/blast1-out.txt', 'w')
    fp.write(out)
    fp.close()

    if err and err.strip():
        fp = open(tempdir + '/blast1-err.txt', 'w')
        fp.write(err)
        fp.close()

    results = list(blastparser.parse_string(out))

    dbfile = '/scratch/titus/mssm/genome.masked.fasta'
    newfile = tempdir + '/' + 'query.fa'

    if seqtype == 'protein':
        program = 'tblastn'
    else:
        program = 'blastn'
        
    out, err = blastkit.run_blast(program, newfile, dbfile, args=['-e 1e-6'])

    fp = open(tempdir + '/blast2-out.txt', 'w')
    fp.write(out)
    fp.close()

    if err and err.strip():
        fp = open(tempdir + '/blast2-err.txt', 'w')
        fp.write(err)
        fp.close()

    results = list(blastparser.parse_string(out))

    dbfile = '/scratch/titus/mssm/maker-genes.fa'
    newfile = tempdir + '/' + 'query.fa'

    if seqtype == 'protein':
        program = 'tblastn'
    else:
        program = 'blastn'
        
    out, err = blastkit.run_blast(program, newfile, dbfile, args=['-e 1e-6'])
    
    fp = open(tempdir + '/blast3-out.txt', 'w')
    fp.write(out)
    fp.close()

    if err and err.strip():
        fp = open(tempdir + '/blast3-err.txt', 'w')
        fp.write(err)
        fp.close()

    results = list(blastparser.parse_string(out))

    fp = open(tempdir + '/index.html', 'w')
    fp.write('BLAST complete. <p>')
    fp.write('See <a href="blast1-out.txt">mRNAseq blast output.</a><p>')
    fp.write('See <a href="blast2-out.txt">genome blast output.</a><p>')
    fp.write('See <a href="blast3-out.txt">predicted genes blast output.</a><p>')
    fp.write('<p>')

    ###

    fp.close()
    return

    #db = seqdb.SequenceFileDB(dbfile)

    for query in results:
        for subject in query:
            for hit in subject:
                fp.write('Query: %s; subject: %s; hit, e_val: %s' % \
                         (query.query_name,
                          subject.subject_name,
                          hit.expect))
                fp.write('<br>')

                continue
                # @CTB
                seq = db[subject.subject_name]
                seq = str(seq)

                fp.write('sequence: %s' % (seq,))
                fp.write('<p>')

    ###

    fp.close()

###

try:
    do_cgi()
except SystemExit:
    pass
except:                                 # catch errors & write them out
    print 'Content-type: text/html\n'
    print '<pre>'
    print traceback.format_exc()
    print '</pre>'

