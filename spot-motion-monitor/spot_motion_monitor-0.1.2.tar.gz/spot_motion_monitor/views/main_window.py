#------------------------------------------------------------------------------
# Copyright (c) 2018 LSST Systems Engineering
# Distributed under the MIT License. See LICENSE for more information.
#------------------------------------------------------------------------------
import sys

from PyQt5 import QtGui
from PyQt5 import QtWidgets

from spot_motion_monitor.views import Ui_MainWindow
from spot_motion_monitor import __version__

__all__ = ['main']

class SpotMotionMonitor(QtWidgets.QMainWindow, Ui_MainWindow):

    def __init__(self, parent=None):
        super(SpotMotionMonitor, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("Spot Motion Monitor")

        self.set_action_icon(self.actionExit, "exit.svg", True)

        self.actionExit.triggered.connect(self.close)
        self.actionAbout.triggered.connect(self.about)

    def about(self):
        """This function presents the about dialog box.
        """
        about = QtWidgets.QMessageBox()
        about.setIconPixmap(QtGui.QPixmap(":smm_logo_sm.png"))
        about.setWindowTitle("About the Spot Motion Monitor")
        about.setStandardButtons(QtWidgets.QMessageBox.Ok)
        about.setInformativeText('''
                                 <b>Spot Motion Monitor</b> v{}
                                 <p>
                                 This application is the front-end for a systems that
                                 monitors seeing within a telescope dome.
                                 </p>
                                 <br><br>
                                 Copyright 2018 LSST Systems Engineering
                                 '''.format(__version__))
        about.exec_()

    def set_action_icon(self, action, icon_name, icon_in_menu=False):
        """Setup the icon for the given action.

        Parameters
        ----------
        action : QAction
          A specific program action.
        icon_name : str
          Name of the icon in the QRC file.
        icon_in_menu : bool, optional
          Make the icon visible in the program menu.
        """
        action.setIcon(QtGui.QIcon(QtGui.QPixmap(':{}'.format(icon_name))))
        action.setIconVisibleInMenu(icon_in_menu)


def main():
    """
    This is the entrance point of the program
    """
    app = QtWidgets.QApplication(sys.argv)
    app.setOrganizationName("LSST-Systems-Engineering")
    app.setOrganizationDomain("lsst.org")
    app.setApplicationName("Spot Motion Monitor")
    form = SpotMotionMonitor()
    form.show()
    app.exec_()
