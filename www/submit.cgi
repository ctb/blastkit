#! /usr/bin/python
import cgitb
cgitb.enable()

import sys
import shutil
import cPickle
import traceback
import os, os.path
import time
import jinja2

import _mypath
import blastkit
import blastkit_config
import blastparser
import screed

import cgi

###

# this sets up jinja2 to load templates from the 'templates' directory
templates_dir = blastkit_config._basedir('templates')
loader = jinja2.FileSystemLoader(templates_dir)
env = jinja2.Environment(loader=loader)

PLACEHOLDER_MESSAGE = env.get_template('waiting-for-blast.html').render()

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

    import screed
    query_data = list(screed.open(newfile))
    assert len(query_data) == 1
    query_data = query_data[0]
    query_seq = query_data.sequence
    query_name = query_data.name
    query_descr = query_data.description
    query_len = len(query_seq)

    query_seq = query_seq.lower()
    dna = query_seq.count('a') + query_seq.count('t') + query_seq.count('g') + query_seq.count('c')
    if dna / float(query_len) > 0.75:
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

    # some utility vars/functions for the template to use --
    db = screed.ScreedDB(dbfile)

    def get_record(subject_match):
        return db[subject_match.subject_name]

    total_matches = 0
    if len(results):
       total_matches = len(results[0])

    fp = open(tempdir + '/index.html', 'w')
    template = env.get_template('blast_render.html')
    fp.write(template.render(locals()))
    fp.close()

    ###

    import screed
    import screed.pygr_api
    import pygr_draw
    from pygr_draw import Annotation

    screed.read_fasta_sequences(tempdir + '/query.fa')
    db = screed.pygr_api.ScreedSequenceDB(tempdir + '/query.fa')

    image = pygr_draw.Draw(tempdir + '/image.png')
    colors = image.colors

    annots = []
    record = results[0]
    for hits in record:
        for match in hits:
            start = min(match.query_start, match.query_end)
            end = max(match.query_start, match.query_end)
            annots.append(Annotation(hits.subject_name, record.query_name,
                                     start, end, color=colors.blue))

    image.add_track(annots, db)

    image.save(db[query_name])

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
