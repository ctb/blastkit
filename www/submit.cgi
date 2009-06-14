#! /Users/t/dev/env/bin/python
import sys
import shutil
import cPickle
import traceback
import os, os.path
import time

import _mypath
import blastkit
import blastparser

import cgi

def do_cgi():
    """
    Main CGI function.  Shoud retrieve 
    """
    form = cgi.FieldStorage()

    sequence = form['sequence'].value
    
    tempdir, dirstub = blastkit.make_dir()

    fp = open('%s/query.fa' % (tempdir,), 'w')
    fp.write('>query_seq\n%s\n' % (sequence,))
    fp.close()

    fp = open('%s/index.html' % (tempdir,), 'w')
    fp.write('''
    <head><META http-equiv="refresh" content="5;"></head>
    <body>
    This page will automatically reload, and the results will be available here.  
    If you get a blank page, hit Reload on your browser.
    Results for large datasets can take up to 20 minutes to be returned ...
    <p>
    %s
    </body>
    ''' % tempdir)
    fp.close()

    blastkit.split_execution(response_fn, (dirstub,), worker_fn, (tempdir,))

def response_fn(dirstub):
    name = os.environ['SERVER_NAME']
    port = os.environ['SERVER_PORT']
    path = os.path.dirname(os.environ['SCRIPT_NAME'])
    
    url = 'http://%s:%s%s/files/%s' % (name, port, path, dirstub)

    time.sleep(1)
    
    print 'Location: %s\n' % (url,)

def worker_fn(tempdir):
    try:
        dbfile = '/Users/t/dev/blastkit/gapping.fa'
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
        fp.write('Done.  <a href="blast-out.txt">blast output</a>')
        fp.close()
    except:
        fp = open(tempdir + '/err.txt', 'w')
        fp.write(traceback.format_exc())
        fp.close()

###

try:
    do_cgi()
except SystemExit:
    pass
except:
    print 'Content-type: text/html\n'
    print '<pre>'
    print traceback.format_exc()
    print '</pre>'

