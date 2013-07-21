#! /usr/bin/env python
import glob, os.path, sys

def check_shebangs():
    cgipath = os.path.dirname(__file__)
    cgipath = os.path.join(cgipath, 'www')
    cgipath = os.path.join(cgipath, '*.cgi')

    all_good = True

    cgilist = glob.glob(cgipath)
    for filename in cgilist:
        firstline = open(filename).readline()
        firstline = firstline[2:].strip()
        if firstline != sys.executable:
            print 'ERROR: %s does not have correct python executable, %s' %\
                (filename, sys.executable)
            all_good = False

    return all_good

def main():
    all_good = True
    
    if not check_shebangs():
        all_good = False

    if not all_good:
        sys.exit(-1)

if __name__ == '__main__':
    main()

