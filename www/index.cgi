#! /usr/bin/python
import cgitb
cgitb.enable()

import sys
import _mypath
try:
    import blastkit_config
except ImportError:
    print 'Content-type: text/html\n\n<pre>Cannot import blastkit_config</pre>'
    sys.exit(-1)

# this sets up jinja2 to load templates from the 'templates' directory
import jinja2
templates_dir = blastkit_config._basedir('templates')
loader = jinja2.FileSystemLoader(templates_dir)
env = jinja2.Environment(loader=loader)

print 'Content-type: text/html\n\n'

dblist = []
for db in blastkit_config.databases:
    html = "<option value='%(id)s'>%(name)s (%(seqtype)s)</option>" % db
    dblist.append(html)

html = "Database: <select name='db'>%s</select>" % "\n".join(dblist)

print env.get_template('index.html').render(dict(databases=html))
