#! python
# -*- coding: utf-8 -*-

"""Main GUI script.

Authors:
    Victor Hugo de Mello Pessoa <victor.pessoa@usp.br>
    Daniel Cosmo Pizetta <daniel.pizetta@usp.br>

Since:
    2017/07/01

"""

import logging
import sys

from pyqtgraph.Qt import QtGui

from mrsprint import __version__ as version
from mrsprint import project, org_name, org_domain
from mrsprint.mainwindow import MainWindow

_logger = logging.getLogger(__name__)


def main():
    app = QtGui.QApplication(sys.argv[1:])
    app.setStyle('Fusion')

    app.setApplicationVersion(version)
    app.setApplicationName(project)
    app.setOrganizationName(org_name)
    app.setOrganizationDomain(org_domain)

    try:
        import qdarkstyle
    except ImportError:
        _logger.info("No dark theme installed, use 'pip install qdarkstyle' to install.")
    else:
        try:
            app.setStyleSheet(qdarkstyle.load_stylesheet_pyside())
        except Exception as err:
            _logger.warning("Problems using qdarkstyle.\nError: %s", str(err))

    window = MainWindow()
    window.setWindowTitle(project + ' v' + version)
    window.showMaximized()
    app.exec_()


if __name__ == "__main__":
    sys.exit(main())
