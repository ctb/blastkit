import sys
import os
import subprocess
import tempfile
import traceback

BLAST = '/usr/local/bin/blastall'
tempdir = '/Users/t/dev/blastkit/www/files'

###

def run_blast(program, sequence_filename, database_name, args=[]):
    """
    Run BLAST.
    """

    cmd = [ BLAST, '-p', program, '-d', database_name,
            '-i', sequence_filename ]
    cmd.extend(args)

    try:
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
    except OSError:
        return '', traceback.format_exc()
    
    (stdout, stderr) = p.communicate()

    return stdout, stderr

def detach():
    """
    Returns result of os.fork() -- should exit when non-zero, continue else.
    """
    x = os.fork()
    if x != 0:
        return x

    # run in child process; daemonize first
    si = file("/dev/null", 'r')
    so = file("/dev/null", 'a+')
    se = file("/dev/null", 'a+', 0)
    os.dup2(si.fileno(), sys.stdin.fileno())
    os.dup2(so.fileno(), sys.stdout.fileno())
    os.dup2(se.fileno(), sys.stderr.fileno())

    os.setsid()

    return x

def split_execution(parent_fn, parent_fn_args, child_fn, child_fn_args):
    """
    Fork, and run parent_fn in the parent process; in the child process,
    detach from the controlling terminal and *then* run the child fn.
    """
    if detach() != 0:
        parent_fn(*parent_fn_args)
    else:
        child_fn(*child_fn_args)
    sys.exit(0)

def make_dir():
    """
    Make a working directory.
    """
    dir = tempfile.mkdtemp('', 'blast.', tempdir)
    dirstub = dir[len(tempdir) + 1:]
    return dir, dirstub
