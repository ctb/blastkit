#! /Users/t/dev/env/bin/python
import _mypath
import blastkit
import sys

print 'Content-type: text/html'
print ''
print 'Hello, world!\n'

if blastkit.detach() != 0:
   sys.exit(0)

import time
time.sleep(10)
open('/tmp/HI', 'w').write("%s" % (time.time(),))
