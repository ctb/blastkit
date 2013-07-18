#! /home/t/blastkit/bk.lamprey/env/bin/python
import cgitb
cgitb.enable()

import sys
import _mypath
try:
    import blastkit_config
except ImportError:
    print 'Content-type: text/html\n\n<pre>Cannot import blastkit_config</pre>'
    sys.exit(-1)

print 'Content-type: text/html\n\n'

dblist = []
for db in blastkit_config.databases:
    html = "<option value='%(id)s'>%(name)s (%(seqtype)s)</option>" % db
    dblist.append(html)

html = "Database: <select name='db'>%s</select>" % "\n".join(dblist)

print '''\
<h1>BLAST</h1>

<p>

<form method='POST' action='submit.cgi'>
Sequence name: <input type='text' name='name' value='query'><p>
Sequence:<br>
<textarea name='sequence' rows='30' cols='60'></textarea>
<p>
%(databases)s
<p>
<input type='submit' value='Run BLAST'>
<p>
<h2>More parameters:</h2>
<p>
Program: <select name='program'>
<option value='auto'>(auto)</option>
<option value='blastn>BLASTN (DNA x DNA)</option>
<option value='blastp'>BLASTP (protein x protein)</option>
<option value='blastx'>BLASTX (DNA x protein)</option>
<option value='tblastn'>TBLASTN (protein x DNA)</option>
<option value='tblastx'>TBLASTX (translated DNA x translated DNA)</option>
</select>
<p>
E-value cutoff: <input type='text' name='cutoff' value='1e-3'>
</form>
''' % dict(databases=html)
