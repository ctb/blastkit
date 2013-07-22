#! /home/t/blastkit/env/bin/python
import cgitb
cgitb.enable()

import sys, os
import _mypath
try:
    import blastkit_config
except ImportError:
    print 'Content-type: text/html\n\n<pre>Cannot import blastkit_config</pre>'
    sys.exit(-1)

import cgi
import screed
import whoosh
from whoosh.qparser import MultifieldParser

# this sets up jinja2 to load templates from the 'templates' directory
import jinja2
templates_dir = blastkit_config._basedir('templates')
loader = jinja2.FileSystemLoader(templates_dir)
env = jinja2.Environment(loader=loader)

# retrieve sequence from submitted form info, if any
form = cgi.FieldStorage()

query = ''
if 'query' in form:
    query = form['query'].value
database = None
if 'db' in form:
    database = form['db'].value

dbinfo = blastkit_config.databases[0]
for _dbi in blastkit_config.databases:
    if _dbi['id'] == database:
        dbinfo = _dbi

dbfile = dbinfo['filename']

###

dblist = []
for db in blastkit_config.databases:
    selected = ""
    if db == dbinfo:
        selected = " selected"

    d = dict(db)
    d['selected'] = selected

    html = "<option value='%(id)s'%(selected)s>%(name)s (%(seqtype)s)</option>" % d
    dblist.append(html)

html = "Database: <select name='db'>%s</select>" % "\n".join(dblist)

###

results = []
indexdir = dbfile + '.whooshd'

index_dne = True
if os.path.isdir(indexdir):
    index_dne = False

if query and not index_dne:
    ix = whoosh.index.open_dir(indexdir, readonly=True)

    seqdb = screed.ScreedDB(dbfile)

    with ix.searcher() as searcher:
        q = MultifieldParser(["name", "description"],
                                  ix.schema).parse(query)
        res = searcher.search(q, limit=100)

        for r in res:
            key = r['name']
            record = seqdb[key]
            results.append(record)

###

print 'Content-type: text/html\n'
print env.get_template('search.html').render(dict(databases=html,
                                                  query=query,
                                                  results=results,
                                                  dbinfo=dbinfo,
                                                  index_dne=index_dne))
