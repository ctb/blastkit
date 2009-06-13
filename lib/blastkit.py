import sys
import os
import subprocess

def run_blast(program, sequence_filename, database_name,
              args=[]):

    cmd = [ 'blastall', '-p', program, '-d', database_name,
            '-i', sequence_filename ]
    cmd.extend(args)

    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
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
