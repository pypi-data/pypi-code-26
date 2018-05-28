#!/usr/bin/env python
import sys, os, decida.test, string

test_dir = decida.test.test_dir()
tests = decida.test.test_list()
skip_tests = ("test_Calc_2", "test_Fitter", "test_LevMar", "test_StatusDialog", "test_Tckt_1", "test_TextWindow")

print "@" * 70
print " exit graphical tests by closing the window, unless otherwise noted ..."
print " don't exit by \"File->Exit DeCiDa\" (DataViewm tests)"
print "@" * 70

for test in tests :
    if test in skip_tests :
        print "@" * 70
        print " skipping ", test, ":"
        print " try this test separately"
        print "@" * 70
        continue
    print " ... %s ... " % (test)
    if test == "test_FrameNotebook_1":
        print "@" * 70
        print " ", test, ":"
        print "  do not press \"QUIT\" to exit ..."
        print "  press each \"CONTINUE\" button ..."
        print "  exit this test by pressing \"EXIT\" when it appears ..."
        print "@" * 70
    elif test == "test_FrameNotebook_2":
        print "@" * 70
        print " ", test, ":"
        print "  do not press \"QUIT\" to exit ..."
        print "  press each \"CONTINUE\" button ..."
        print "@" * 70
    elif test in ("test_NGspice_1", "test_NGspice_2", "test_NGspice_3") :
        print "@" * 70
        print " ", test, ":"
        print "  press \"Simulate/Plot\" to run simulation ..."
        print "  close window to exit test"
        print "@" * 70
    execfile("%s/%s.py" % (test_dir, test))
