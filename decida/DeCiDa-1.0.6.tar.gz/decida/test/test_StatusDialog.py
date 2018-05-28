#! /usr/bin/env python

import decida, sys, os.path, re, string, time, glob
from decida.StatusDialog import *
import threading

class ProgressReport() :
    def __init__(self):
        self._iter = 0
        self._report = None
        self._report_ready = False
        self._thread = threading.Thread(target=self._generate_report, args=())
        self._thread.setDaemon(True)
        self._thread.start()
    def _generate_report(self):
        while True:
            if self._report_ready : continue
            self._iter += 1
            #utput = decida.syscall("/usr/bin/top -l 1")
            output = decida.syscall("/bin/ps -ax")
            lines = string.split(output, "\n")
            lines.append(" iteration: %s" % (self._iter))
            self._report = string.join(lines, "\n")
            self._report_ready = True
    def get_report(self):
        if self._report_ready :
            self._report_ready = False
            return self._report
        else :
            return None

pr = ProgressReport()
sts = StatusDialog(title="top monitor", command=pr.get_report)
