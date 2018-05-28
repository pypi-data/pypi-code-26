#!/usr/bin/env python
import user, decida, decida.test
from decida.Data import Data
from decida.XYplotm import XYplotm

test_dir = decida.test.test_dir()
d = Data()
d.read(test_dir + "smartspice_tr_binary.raw")
xyplot=XYplotm(None, command=[d, "time v(cint)"])
