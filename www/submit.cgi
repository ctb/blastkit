#! /u/t/dev/venv/bin/python
import sys
import shutil
import cPickle
import traceback
import os, os.path
import time
import screed

import _mypath
import blastkit
import blastparser
from pygr import seqdb

import cgi

##

EVALUE = "1e-6"
EVALUE_STR = "-e " + EVALUE

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
                             worker_fn, (tempdir, seqtype))

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
def worker_fn(tempdir, seqtype):
    """
    Run the BLAST and display the results.
    """
    dbfile = '/scratch/titus/mssm/pm-abund.k31.200.num.fa'
    newfile = tempdir + '/' + 'query.fa'

    if seqtype == 'protein':
        program = 'tblastn'
    else:
        program = 'blastn'
        
    out1, err = blastkit.run_blast(program, newfile, dbfile, args=[EVALUE_STR])

    fp = open(tempdir + '/blast1-out.txt', 'w')
    fp.write(out1)
    fp.close()

    if err and err.strip():
        fp = open(tempdir + '/blast1-err.txt', 'w')
        fp.write(err)
        fp.close()

    results1 = list(blastparser.parse_string(out1))

    matches1 = extract_matches(results1, dbfile)
    fp = open(tempdir + '/blast1-matches.txt', 'w')
    write_matches_to_file(matches1, fp)
    fp.close()

    dbfile = '/scratch/titus/mssm/genome.masked.fasta'
    newfile = tempdir + '/' + 'query.fa'

    if seqtype == 'protein':
        program = 'tblastn'
    else:
        program = 'blastn'
        
    out2, err = blastkit.run_blast(program, newfile, dbfile, args=[EVALUE_STR])

    fp = open(tempdir + '/blast2-out.txt', 'w')
    fp.write(out2)
    fp.close()

    if err and err.strip():
        fp = open(tempdir + '/blast2-err.txt', 'w')
        fp.write(err)
        fp.close()

    results2 = list(blastparser.parse_string(out2))

    dbfile = '/scratch/titus/mssm/maker-genes.fa'
    newfile = tempdir + '/' + 'query.fa'

    if seqtype == 'protein':
        program = 'tblastn'
    else:
        program = 'blastn'
        
    out3, err = blastkit.run_blast(program, newfile, dbfile, args=[EVALUE_STR])
    
    fp = open(tempdir + '/blast3-out.txt', 'w')
    fp.write(out3)
    fp.close()

    if err and err.strip():
        fp = open(tempdir + '/blast3-err.txt', 'w')
        fp.write(err)
        fp.close()

    results3 = list(blastparser.parse_string(out3))
    
    matches3 = extract_matches(results3, dbfile)
    fp = open(tempdir + '/blast3-matches.txt', 'w')
    write_matches_to_file(matches3, fp)
    fp.close()

    ##

    dbfile = '/scratch/titus/mssm/maker-genes.prot.fa'
    newfile = tempdir + '/' + 'query.fa'

    if seqtype == 'protein':
        program = 'blastp'
    else:
        program = 'blastx'
        
    out4, err = blastkit.run_blast(program, newfile, dbfile, args=[EVALUE_STR])
    
    fp = open(tempdir + '/blast4-out.txt', 'w')
    fp.write(out4)
    fp.close()

    if err and err.strip():
        fp = open(tempdir + '/blast4-err.txt', 'w')
        fp.write(err)
        fp.close()

    results4 = list(blastparser.parse_string(out4))
    
    matches4 = extract_matches(results4, dbfile)
    fp = open(tempdir + '/blast4-matches.txt', 'w')
    write_matches_to_file(matches4, fp)
    fp.close()

    #query_record = list(screed.fasta.fasta_iter(open(tempdir + '/query.fa')))
    ###

    fp = open(tempdir + '/index.html', 'w')
    fp.write(TEMPLATE_HEAD)
    fp.write('<div id="content">')
    fp.write('<div id="right">')
    fp.write('<h1>BLAST results:</h1><p>')
    fp.write('<h2>Raw BLAST results</h2><p>')
    fp.write('<a href="blast3-out.txt">MAKER predicted cDNA blast output.</a><p>')
    fp.write('<a href="blast4-out.txt">MAKER predicted protein blast output.</a><p>')
    fp.write('<a href="blast1-out.txt">mRNAseq blast output.</a><p>')
    fp.write('<a href="blast2-out.txt">Masked genome blast output.</a><p>')
    fp.write('<p>')

    fp.write('<h2>Matched sequences</h2><p>')
    fp.write("<a href='blast3-matches.txt'>MAKER/predicted cDNA matches (FASTA)</a><p>")
    fp.write("<a href='blast4-matches.txt'>MAKER/predicted protein matches (FASTA)</a><p>")
    fp.write("<a href='blast1-matches.txt'>mRNAseq matches (FASTA)</a>")

    fp.write("</div>\n")
    
    fp.write('<div id="left">')
    fp.write('<h1>Summary and Results</h1><p>')

#    fp.write('Query sequence: %s, length %s' % (query_record['name'], len(query_record['sequence'])))
    
    n = 0
    for query in results2:
        for subject in query:
            for hit in subject:
                n += 1
                fp.write('%d. <a href="http://petromyzon.msu.edu/fgb2/gbrowse/sea_lamprey/?name=%s:%s..%s">%s (%s-%s)</a> - %s/score: %s/length: %s<p>\n' % (n, subject.subject_name, hit.subject_start, hit.subject_end, subject.subject_name, hit.subject_start, hit.subject_end, hit.expect, hit.score, len(hit.subject_sequence)))
    
    fp.write("</div>\n")
    
    ###

    fp.write(TEMPLATE_FOOT)

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

def extract_matches(blast_results, dbfile):
    db = seqdb.SequenceFileDB(dbfile)

    x = []
    for query in blast_results:
        for subject in query:
            for hit in subject:
                seq = db[subject.subject_name]
                seq = str(seq)
                x.append((subject.subject_name, seq))

    return x

def write_matches_to_file(matches, fp):
    for name, seq in matches:
        fp.write('>%s\n' % (name,))
        for i in range(0, len(seq), 60):
            fp.write('%s\n' % seq[i:i+60])

###

TEMPLATE_HEAD="""

<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/x
html1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
<title>Lamprey SuperBlastGeneSearch</title>
<link rel="stylesheet" type="text/css" href="../../style.css" media="screen" />
<script type="text/javascript" src="jquery-1.4.3.min.js"></script>

<script type="text/javascript">

$(document).ready(function(){

  $("#dnaEx").click(function(event) { 
     $("#name").val("pmfoxA ");
     $("#sequence").val("ATGATGACCCTCAACGAGATCTACTCGTGGATCATGGACCTCTTCCCCTTCTACCGGCAGAACCAGCAGCGCTGGCAGAACTCCATCCGCCACTCGCTCTCCTTCAACGACTGCTTCGTCAAGGTGCCGCGCTCGCCCGACAAGCCGGGCAAGGGCTCCTTCTGGGCGCTCCACCCGGACTCGGGGAACATGTTCGAGAACGGCTGCTACCTGCGGCGGCAGAAGCGCTTCAAGTGCGACAGGAAGCAGAAGA");
     $("#seqtype").val("DNA");
     event.preventDefault();
  });

  $("#protEx").click(function(event) { 
     $("#name").val("MmEngrailed");
     $("#sequence").val("MEEQQPEPKSQRDSGLGAVAAAAPSGLSLSLSPGASGSSGSDGDSVPVSPQPAPPSPPAAPCLPPLAHHPHLPPHPPPPPPPPPPPPQHLAAPAHQPQPAAQLHRTTNFFIDNILRPDFGCKKEQPLPQLLVASAAAGGGAAAGGGSRVERDRGQTGAGRDPVHSLGTRASGAASLLCAPDANCGPPDGSQPATAVGAGASKAGNPAAAAAAAAAAAAAAVAAAAAAASKPSDSGGGSGGNAGSPGAQGAKFPEHNPAILLMGSANGGPVVKTDSQQPLVWPAWVYCTRYSDRPSSGPRTRKLKKKKNEKEDKRPRTAFTAEQLQRLKAEFQANRYITEQRRQTLAQELSLNESQIKIWFQNKRAKIKKATGIKNGLALHLMAQGLYNHSTTTVQDKDESE");
     $("#seqtype").val("protein");
     event.preventDefault();
  });

 });
      
</script>

</head>
<body>
<div id="header">
<h1>Lamprey SuperBlastGeneSearch</h1>
<!-- <div id="menu">
  <ul id="nav">
   <li><a href="#">Home</a></li>
   <li><a href="#">About Me</a></li>
   <li><a href="#">Archives</a></li>
   <li><a href="#">Sitemap</a></li>
  </ul>
 </div>
-->
</div>

<div id="content">
"""

TEMPLATE_FOOT="""
</div>

</body>
</html>
"""

if __name__ == '__main__':
    try:
        do_cgi()
    except SystemExit:
        pass
    except:                                 # catch errors & write them out
        print 'Content-type: text/html\n'
        print '<pre>'
        print traceback.format_exc()
        print '</pre>'
