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
This page will automatically reload, and the results will be available here.
<p>
If you get a blank page, hit Reload on your browser.
Results for large datasets can take up to 20 minutes to be returned ...
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
    sequence = form['sequence'].value

    # make a working directory to save stuff in
    tempdir, dirstub = blastkit.make_dir()

    # write out the query sequence
    fp = open('%s/query.fa' % (tempdir,), 'w')
    fp.write('>%s\n%s\n' % (name, sequence,))
    fp.close()

    # write out the placeholder message
    fp = open('%s/index.html' % (tempdir,), 'w')
    fp.write(PLACEHOLDER_MESSAGE)
    fp.close()

    # fork response function / worker function
    blastkit.split_execution(response_fn, (dirstub,), worker_fn, (tempdir,))

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
def worker_fn(tempdir):
    """
    Run the BLAST and display the results.
    """
    dbfile = '/u/t/dev/blastkit/db/MA1W2.fa'
    newfile = tempdir + '/' + 'query.fa'

    out, err = blastkit.run_blast('blastn', newfile, dbfile)

    fp = open(tempdir + '/blast-out.txt', 'w')
    fp.write(out)
    fp.close()

    if err and err.strip():
        fp = open(tempdir + '/blast-err.txt', 'w')
        fp.write(err)
        fp.close()

    results = list(blastparser.parse_string(out))

    fp = open(tempdir + '/blast-results.pickle', 'w')
    cPickle.dump(results, fp)
    fp.close()

    fp = open(tempdir + '/index.html', 'w')
    fp.write('BLAST complete. <p>')
    fp.write('See <a href="blast-out.txt">blast output.</a>')
    fp.write('<p>')

    ###

    db = seqdb.SequenceFileDB(dbfile)

    for query in results:
        for subject in query:
            for hit in subject:
                fp.write('Query: %s; subject: %s; hit, e_val: %s' % \
                         (query.query_name,
                          subject.subject_name,
                          hit.expect))
                fp.write('<br>')

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

