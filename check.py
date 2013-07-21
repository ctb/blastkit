#! /usr/bin/env python
import glob, os.path, sys
import os
import stat

thisdir = os.path.dirname(__file__)
cgipath = os.path.join(thisdir, 'www')
libpath = os.path.join(thisdir, 'lib')

def check_shebangs():
    all_good = True

    cgifiles = os.path.join(cgipath, '*.cgi')
    cgilist = glob.glob(cgifiles)
    for filename in cgilist:
        firstline = open(filename).readline()
        firstline = firstline[2:].strip()
        if firstline != sys.executable:
            print 'ERROR: %s does not have correct python executable, %s' %\
                (filename, sys.executable)
            all_good = False

    return all_good

def check_www_mypath():
    sys.path.insert(0, cgipath)
    import _mypath

    a = os.path.abspath(_mypath.dir)
    b = os.path.abspath(libpath)

    if a != b:
        print 'ERROR: www/_mypath.py contains inconsistent "dir" variable.'
        print 'dir is: "%s"' % a
        print 'dir should be: "%s"' % b
        print 'please edit!'
        return False

    return True

def check_blastkit_config():
    # run this after check_www_mypath
    import blastkit_config

    all_good = True
    
    if not blastkit_config.BASEDIR.startswith('/'):
        print 'ERROR: BASEDIR in lib/blastkit_config.py must be an absolute path'
        all_good = False

    a = os.path.abspath(blastkit_config.BASEDIR)
    b = os.path.abspath(thisdir)

    if a != b:
        print 'ERROR: BASEDIR in lib/blaskit_config.py is incorrect.'
        print 'Should resolve to: %s' % b
        print 'Actually resolves to: %s' % a
        all_good = False

    if not os.path.exists(blastkit_config.blastkit.BLAST):
        print 'ERROR: blastkit_config BLAST setting is not correct.'
        print 'Currently: %s' % blastkit_config.blastkit.BLAST
        all_good = False

    return all_good

def check_www_files():
    import blastkit_config

    all_good = True

    files_path = os.path.abspath(blastkit_config.blastkit.tempdir)
    if not os.path.isdir(files_path):
        print 'ERROR, tempdir does not exist.'
        print 'Configured as: %s' % blastkit_config.blastkit.tempdir
        print 'Resolves to: %s' % files_path
        print 'Please create/reconfigure!'
        all_good = False
    else:
        st = os.stat(files_path)
        if st.st_mode & stat.S_IROTH and \
                st.st_mode & stat.S_IWOTH and \
                st.st_mode & stat.S_IXOTH:
            pass
        else:
            print 'ERROR, tempdir must be readable, writable, and executable'
            print 'by others.  Please fix!'
            print 'You can do: "chmod o+rwxt %s"' % files_path
            all_good = False

    return all_good

def main():
    all_good = True
    
    if not check_shebangs():
        all_good = False

    if not check_www_mypath():
        all_good = False

    if not check_blastkit_config():
        all_good = False

    if not check_www_files():
        all_good = False

    if not all_good:
        sys.exit(-1)

    print "Everything looks good! Nice job configuratin'."

if __name__ == '__main__':
    main()

