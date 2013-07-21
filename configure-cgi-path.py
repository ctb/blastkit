#! /usr/bin/env python
import glob, os.path, sys

def fix_shebang(filename, exepath):
    fp = open(filename)
    firstline = fp.readline()
    rest = fp.read()
    fp.close()

    firstline = firstline[2:].strip()
    if firstline == exepath:
        return False

    firstline = '#! %s\n' % exepath

    fp = open(filename, 'w')
    fp.write(firstline)
    fp.write(rest)
    fp.close()

    return True

def main():
    cgipath = os.path.dirname(__file__)
    cgipath = os.path.join(cgipath, 'www')
    cgipath = os.path.join(cgipath, '*.cgi')

    cgilist = glob.glob(cgipath)
    print 'Using python exe:', sys.executable
    for filename in cgilist:
        if fix_shebang(filename, sys.executable):
            print 'Fixed shebang line for', filename

if __name__ == '__main__':
    main()
