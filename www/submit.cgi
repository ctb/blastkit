#! /home/t/blastkit/bk.lamprey/env/bin/python
import cgitb
cgitb.enable()

import sys
import shutil
import cPickle
import traceback
import os, os.path
import time

import _mypath
import blastkit
import blastkit_config
import blastparser
import screed

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
    database = form['db'].value
    program = form['program'].value
    cutoff = form['cutoff'].value

    dbinfo = blastkit_config.databases[0]
    for _dbi in blastkit_config.databases:
        if _dbi['id'] == database:
            dbinfo = _dbi

    if program not in ('auto', 'blastn', 'blastp', 'blastx', 'tblastn',
                       'tblastx'):
        program = 'auto'

    try:
        cutoff = float(cutoff)
    except TypeError:
        cutoff = 1e-3

    # make a working directory to save stuff in
    tempdir, dirstub = blastkit.make_dir()

    # write out the query sequence
    sequence = sequence.strip()

    fp = open('%s/query.fa' % (tempdir,), 'w')
    if sequence.startswith('>'):
        pass
    else:
        fp.write('>%s\n' % name)

    fp.write('%s\n' % (sequence,))
    fp.close()

    # write out the placeholder message
    fp = open('%s/index.html' % (tempdir,), 'w')
    fp.write(PLACEHOLDER_MESSAGE)
    fp.close()

    # fork response function / worker function
    blastkit.split_execution(response_fn, (dirstub,), worker_fn,
                             (tempdir, dbinfo),
                             dict(program=program, cutoff=cutoff))

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
def worker_fn(tempdir, dbinfo, program='auto', cutoff=1e-3):
    """
    Run the BLAST and display the results.
    """
    
    dbfile = dbinfo['filename']
    newfile = tempdir + '/' + 'query.fa'

    print 'using DB:', dbfile

    orig_program = program
    data = open(newfile).readlines()[1:]
    data = "".join(data)
    data = data.strip().lower()
    dna = data.count('a') + data.count('t') + data.count('g') + data.count('c')
    if dna / float(len(data)) > 0.75:
        query_type = 'dna'
    else:
        query_type = 'protein'

    if dbinfo['seqtype'].lower() == 'dna':
        if query_type == 'dna':
            program = 'blastn'
        else:
            program = 'tblastn'
    else:
        if query_type == 'dna':
            program = 'blastx'
        else:
            program = 'blastp'

    print 'using program:', program, orig_program

    cmd, out, err = blastkit.run_blast(program, newfile, dbfile,
                                  '-e', '%g' % cutoff)

    fp = open(tempdir + '/blast-cmd.txt', 'w')
    fp.write(cmd)
    fp.close()

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
    fp.write('Here is a brief list of the matches together with the matched DNA sequences.<p>')

    ###

    db = screed.ScreedDB(dbfile)

    for query in results:
        for subject in query:
            for hit in subject:
                record = db[subject.subject_name]
                seq = record.sequence

                fp.write('match: %s (%s) -- <b>%s</b>' % \
                         (subject.subject_name, hit.expect,
                          record.description,))
                fp.write('<br>')

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

