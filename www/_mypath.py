import sys
dir = '/home/t/blastkit/bk.lamprey/lib'

if dir not in sys.path:
    sys.path.insert(0, dir)

import blastkit_config
