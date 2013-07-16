import os

import _mypath
import blastkit_config
import blastkit

def db_path(filename):
    dbdir = os.path.join(os.path.dirname(__file__), '../db')
    filename = os.path.join(dbdir, filename)
    return os.path.abspath(filename)

def test_blast():
    x = blastkit.run_blast('blastn', db_path('query-dna.fa'),
                           db_path('test-dna.fa'),)
    cmd, out, err = x
    assert 'comp0_c0_seq1 len=291' in out
    assert not err

rfn_was_called = False
wfn_was_called = False
def test_split_blast():
    global rfn_was_called
    global wfn_was_called

    rfn_was_called = False
    def rfn(dirstub):
        global rfn_was_called
        assert dirstub == 'some param'
        rfn_was_called = True

    wfn_was_called = False
    def wfn(tempdir, dbinfo, program='auto', cutoff='1e-3'):
        global wfn_was_called 
        assert tempdir == 'a'
        assert dbinfo == 'b'
        assert program == 'foo'
        assert cutoff == 'bar'

        wfn_was_called = True

    try:
        def fake_detach():
            return 0            # run child fn, wfn

        real_detach, blastkit.detach = blastkit.detach, fake_detach

        try:
            blastkit.split_execution(rfn, ("some param",),
                                     wfn, ("a", "b"), dict(program='foo',
                                                           cutoff='bar'))
            assert 0
        except SystemExit:      # this is expected and should happen
            pass

        assert wfn_was_called
        assert not rfn_was_called
    finally:                    # reset
        blastkit.detach = real_detach

    rfn_was_called = False
    wfn_was_called = False
    try:
        def fake_detach():
            return 1            # run parent fn, rfn

        real_detach, blastkit.detach = blastkit.detach, fake_detach

        try:
            blastkit.split_execution(rfn, ("some param",),
                                     wfn, ("a", "b"), dict(program='foo',
                                                           cutoff='bar'))
            assert 0
        except SystemExit:      # this is expected and should happen
            pass

        assert rfn_was_called
        assert not wfn_was_called
    finally:                    # reset
        blastkit.detach = real_detach
