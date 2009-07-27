#! /u/tracyt/env/bin/python
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

from bsddb import btopen
from shelve import BsdDbShelf

from operator import itemgetter

import fasta
                                 


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

    item=form["filename"]
    input_filename = item.filename
                
    blastdb = form['blastdb'].value

    blast_program = form['blastprogram'].value



    # If neither a sequence or a file is submitted, request them

#    print 'Content-type: text/html\n\n'
#    print form.keys()
#    print form['filename']
#    print 'data'
#    print data

    if (not input_filename and not sequence):
        print "Content-type: text/html\n"
        print 'Please upload a file or submit a sequence'
        sys.exit(2)

    # If both are submitted, ask that they submit only one

    if (input_filename and sequence):
        print "Content-type: text/html\n"
        print 'Please only submit a file or a sequence'
#        print 'data:%s:' % len(data)
        sys.exit(2)

    # make a working directory to save stuff in
    tempdir, dirstub = blastkit.make_dir()

    # If a single sequence is submitted
    if form.has_key("sequence"):

        if len(name) > 0:
            # write out the query sequence
            fp = open('%s/query.fa' % (tempdir,), 'w')
            fp.write('>%s\n%s\n' % (name, sequence,))
            fp.close()

        elif (len(sequence) > 0 and len(name) < 0):
            print "Content-type: text/html\n"
            print "Please enter a Query name\ni"
            sys.exit(2)




    # if it's a file that's uploaded instead
    if input_filename:
        data = item.file


        try:
            blast_input = open("%s/query.fa" % (tempdir), 'w')
        except:
            print "Content-type: text/html\n"
            print 'Cannot open', blast_input, 'for writing'
            sys.exit(2)


        try:
            fasta_data = fasta.load(data)
        except:
            print "Content-type: text/html\n"
            print 'This file does not seem to be a fasta file.  Please try again with a fasta file'
            sys.exit(0)

        for key in fasta_data:
            blast_input.write('>%s\n%s\n' % (key, fasta_data[key]))
        blast_input.close()




    # write out the placeholder message
    fp = open('%s/index.html' % (tempdir,), 'w')
    fp.write(PLACEHOLDER_MESSAGE)
    fp.close()

    # fork response function / worker function
    blastkit.split_execution(response_fn, (dirstub,), worker_fn, (tempdir,blastdb,blast_program,))

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
def worker_fn(tempdir, blastdb, blast_program):
    """
    Run the BLAST and display the results.
    """

#    dbfile = '/u/tracyt/blastkit/db_raw/MA1W2.fa'
    dbfile = '/u/tracyt/blastkit/db/' + blastdb + '.fa'
    newfile = tempdir + '/' + 'query.fa'

    out, err = blastkit.run_blast(blast_program, newfile, dbfile)

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



    ###

    db = seqdb.SequenceFileDB(dbfile)

    hit_dict = {}
    hit_dict_query = {}
    hit_dict_blast = {}
    hit_dict_seq = {}

# Take this out for now since we're not matching to an identity database
#    blast_path = '/u/tracyt/blastkit/www/' + blastdb + '.db'

#    _db = btopen(blast_path, 'r')

#    db_blast = BsdDbShelf(_db)

    # For each initial query sequence


    fasta_in = open(tempdir +'/query.fa', 'r')

    fasta_data_raw = fasta.load(fasta_in)

    for i in fasta_data_raw:
        id = i.split
        fasta_data[id[0]] = fasta_data_raw[1]

    
    fp = open(tempdir + '/index.html', 'w')

    fp.write('fasta %s'% (fasta_data))
    
    for query in results:
#        flag = 0
        # For each match in the query
        for subject in query:
            flag = 0
#            fp.write('subject %s' % subject)
            for hit in subject:
#                fp.write ('hit %s' % (hit.expect))
                if (hit.expect < 0.01):         
                    for keys in hit_dict:                    
                        if subject.subject_name == keys:
                            flag = 1
                    if flag == 0:
                        hit_dict[subject.subject_name] = hit.expect
                        hit_dict_query[subject.subject_name] = query.query_name
#                        hit_dict_seq[subject.subject_name] = fasta_data[query.query_name]


# Commenting out section that returns identity for now

                        # Pull out the identity of that sequence from the blast results database
#                        for match in db_blast:
#                            match_list = []
#                            record = db_blast[match]
#                            if len(record) > 1:
#                                if subject.subject_name == match:
#                                    for j in record:
#                                        match_list.append(j)
#                                    hit_dict_blast[subject.subject_name] = match_list


        sorted_hits = sorted(hit_dict.iteritems(), key=itemgetter(1))


#    fp = open(tempdir + '/index.html', 'w')
    fp.write('BLAST complete. <p>')
    fp.write('See <a href="blast-out.txt">blast output.</a> <p>')
    fp.write('See <a href="sequences.fa">FASTA file for blast</a><br>To download this file, Control+click on the file, and use Save Linked File As or Download Linked File As. <br>Use this file to blast your results against nr at the blast website: <a href=http://blast.ncbi.nlm.nih.gov/>http://blast.ncbi.nlm.nih.gov/</a>')
    fp.write('<p>')

    of = open(tempdir + '/sequences.fa', 'w')


    for unique_hits in sorted_hits:
        print_hit = unique_hits[0]
        fp.write('Query sequence: %s<br> Match: %s; E_value: %s' % \
                 (hit_dict_query[print_hit], print_hit,unique_hits[1]))
        fp.write('<br>')

        seq = db[unique_hits[0]]
        seq = str(seq)

#        fp.write('Query sequence: %s' % (hit_dict_seq[print_hit]))
        fp.write('Sequence: %s' % (seq,))
        fp.write('<p>')

        of.write('>%s\n%s\n' % (print_hit, seq,))

# Commenting out section that returns identity for now

#        fp.write('Identity:')
#        for i in hit_dict_blast:
#            if i == print_hit:
#                fp.write('%s<br>br' % hit_dict_blast[print_hit])
#        fp.write('<p>')

                
    ###

    fp.close()
    of.close()

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

