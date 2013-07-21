# EDIT ME: change 'dir' to the full pathname of your blastkit's lib/ directory.
# note: cannot use __file__ to construct lib path here, because this
# file should be linked into or copied into a Web-accessible directory.
dir = '/home/t/blastkit/bk.dev/lib'

import sys

if dir not in sys.path:
    sys.path.insert(0, dir)

import blastkit_config
