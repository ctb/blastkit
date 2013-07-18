#! /home/t/blastkit/bk.dev/env/bin/python
import cgitb
cgitb.enable()

import sys
import _mypath
try:
    import blastkit_config
except ImportError:
    print 'Content-type: text/html\n\n<pre>Cannot import blastkit_config</pre>'
    sys.exit(-1)

import cgi
import screed

# retrieve sequence from submitted form info
form = cgi.FieldStorage()
seqname = form['seqname'].value
database = form['db'].value

dbinfo = blastkit_config.databases[0]
for _dbi in blastkit_config.databases:
    if _dbi['id'] == database:
        dbinfo = _dbi

dbfile = dbinfo['filename']
db = screed.ScreedDB(dbfile)
record = db[seqname]

print 'Content-type: text/html\nContent-Disposition: attachment; filename="blast-results.txt"\n\n>%s\n%s\n' % (record.name, record.sequence)
