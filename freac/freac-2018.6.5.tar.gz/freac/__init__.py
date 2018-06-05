#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from PyQt5 import QtWidgets


def pyqt2bool(entry):
    return not (entry == 'false' or not entry)


def freac():
    app = QtWidgets.QApplication(sys.argv)
    app.setOrganizationName('ESRF')
    app.setOrganizationDomain('www.esrf.eu')
    app.setApplicationName('freac')
    from freac.wfreac import WFreac
    wfreac = WFreac()
    wfreac.show()
    sys.exit(app.exec_())


def inspecteur():
    app = QtWidgets.QApplication(sys.argv)
    app.setOrganizationName('ESRF')
    app.setOrganizationDomain('www.esrf.eu')
    app.setApplicationName('inspect')
    from freac.winspect import WInspect
    winspect = WInspect()
    winspect.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    if len(sys.argv) > 1:
        inspecteur()
    else:
        freac()
