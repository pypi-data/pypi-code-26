#! python
# -*- coding: utf-8 -*-

"""Module responsible for the configuration of settings of all other modules.

Authors:
    * Victor Hugo de Mello Pessoa <victor.pessoa@usp.br>
    * Daniel Cosmo Pizetta <daniel.pizetta@usp.br>

Since:
    2017/07/01

Todo:
    Insert log inside functions.

"""


import logging

import h5py
import pyqtgraph.parametertree as pt
from pyqtgraph.Qt import QtCore, QtGui

from mrsprint.simulator.simulator import Simulator
from mrsprint.subject.sample import SampleConfig, SampleElementConfig
from mrsprint.system.gradient import Gradient
from mrsprint.system.magnet import InhomogeneityConfig, MagnetConfig
from mrsprint.system.rf import RF

_logger = logging.getLogger(__name__)


class Settings(QtGui.QMainWindow):
    """Main window for settings."""

    def __init__(self, *args, **kwargs):
        super(Settings, self).__init__(*args, **kwargs)
        self.path = QtGui.QLineEdit()

        self.sample_config_group = SampleConfig()
        self.sample_element_config_group = SampleElementConfig()
        self.magnet_config_group = MagnetConfig()
        self.inhomogeneity_config_group = InhomogeneityConfig()
        self.gradient_group = Gradient()
        self.rf_group = RF()
        self.simulator_group = Simulator()

        dock_widget = QtGui.QDockWidget("Settings")

        tree = pt.ParameterTree(dock_widget)
        tree.addParameters(self.sample_config_group)
        tree.addParameters(self.sample_element_config_group)
        tree.addParameters(self.magnet_config_group)
        tree.addParameters(self.inhomogeneity_config_group)
        tree.addParameters(self.gradient_group)
        tree.addParameters(self.rf_group)
        tree.addParameters(self.simulator_group)

        dock_widget.setWidget(tree)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, dock_widget)

        self.toolBar = QtGui.QToolBar(self)
        self.toolBar.setIconSize(QtCore.QSize(32, 32))
        self.addToolBar(QtCore.Qt.BottomToolBarArea, self.toolBar)

        # todo: change to use rc files
        self.actionOpen = QtGui.QAction(self)
        icon_open = QtGui.QIcon()
        icon_open.addPixmap(QtGui.QPixmap("./icons/FileOpen.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionOpen.setIcon(icon_open)
        self.actionOpen.triggered.connect(self.openFile)
        self.toolBar.addAction(self.actionOpen)

        # todo: change to use rc files
        self.actionSave = QtGui.QAction(self)
        icon_save = QtGui.QIcon()
        icon_save.addPixmap(QtGui.QPixmap("./icons/FileSave.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionSave.setIcon(icon_save)
        self.actionSave.triggered.connect(self.saveFile)
        self.toolBar.addAction(self.actionSave)

    def check(self):
        """Evaluate if parameters are between its limits before saving them.

        Returns:
            bool: True if OK.

        Todo:
            Reduce complexity.

        """
        error_message = ""

        # sample
        if self.sample_config_group.maxSizeX.value() < self.sample_config_group.SizeX.value():
            error_message += "'Size X Max' must be greater than or equal to 'Size X Default'\n"
        if self.sample_config_group.maxSizeY.value() < self.sample_config_group.SizeY.value():
            error_message += "'Size Y Max' must be greater than or equal to 'Size Y Default'\n"
        if self.sample_config_group.maxSizeZ.value() < self.sample_config_group.SizeZ.value():
            error_message += "'Size Z Max' must be greater than or equal to 'Size Z Default'\n"
        if self.sample_config_group.maxN.value() < self.sample_config_group.Nx.value():
            error_message += "'Max Number of points' must be greater than 'Nx Default'"
        if self.sample_config_group.maxN.value() < self.sample_config_group.Ny.value():
            error_message += "'Max Number of points' must be greater than 'Ny Default'"
        if self.sample_config_group.maxN.value() < self.sample_config_group.Nz.value():
            error_message += "'Max Number of points' must be greater than 'Nz Default'"
        if (self.sample_element_config_group.maxT1.value() < self.sample_element_config_group.t1.value() or
                self.sample_element_config_group.t1.value() < self.sample_element_config_group.minT1.value()):
            error_message += "'T1 Default' must be in between 'T1 Max Value' and 'T1 Min Value'\n"
        if (self.sample_element_config_group.maxT2.value() < self.sample_element_config_group.t2.value() or
                self.sample_element_config_group.t2.value() < self.sample_element_config_group.minT2.value()):
            error_message += "'T2 Default' must be in between 'T2 Max Value' and 'T2 Min Value'\n"
        if (self.sample_element_config_group.maxRho.value() < self.sample_element_config_group.rho.value() or
                self.sample_element_config_group.rho.value() < self.sample_element_config_group.minRho.value()):
            error_message += "'Rho Default' must be in between 'Rho Max Value' and 'Rho Min Value'\n"

        # magnet
        if self.inhomogeneity_config_group.limitB0x.value() < abs(self.inhomogeneity_config_group.B0x.value()):
            error_message += "'B0x Default' must be in between the limits defined by 'B0x Limit Value'\n"
        if self.inhomogeneity_config_group.limitB0y.value() < abs(self.inhomogeneity_config_group.B0y.value()):
            error_message += "'B0y Default' must be in between the limits defined by 'B0y Limit Value'\n"
        if self.inhomogeneity_config_group.limitB0z.value() < abs(self.inhomogeneity_config_group.B0z.value()):
            error_message += "'B0z Default' must be in between the limits defined by 'B0z Limit Value'\n"

        if error_message:
            error_dialog = QtGui.QMessageBox()
            error_dialog.setWindowTitle("Error in parameters set")
            error_dialog.setText("It was found the following error(s):\n" + error_message)
            error_dialog.exec()
            return False
        else:
            return True

    def saveFile(self):
        """Open a dialog to select the config file to be saved."""
        if not self.check():
            return

        file_dialog = QtGui.QFileDialog(caption="Save settings file...")
        file_dialog.setNameFilter("*.config")
        file_dialog.setAcceptMode(QtGui.QFileDialog.AcceptSave)

        if file_dialog.exec():
            file_path = file_dialog.selectedFiles()[0]

            # todo: there is a better way to do this, use splitext
            if file_path[-7:] != ".config":
                file_path += ".config"

            if file_path:
                self.save(file_path)

    def save(self, file_path):
        """Save a HDF5 settings file.

        Args:
            file_path (str): Path to a file containing the settings.

        """
        file_ = h5py.File(file_path, 'w')
        settings_group = file_.create_group("SettingsGroup")
        simulator = [param.value() for param in self.simulator_group]

        if simulator[0] == "From Start":
            simulator[0] = 0
        elif simulator[0] == "Steady State":
            simulator[0] = 1
        if simulator[1] == "All Points":
            simulator[1] = 0
        elif simulator[1] == "End Points":
            simulator[1] = 1

        # Creating datasets
        settings_group.create_dataset("sample_config", data=[param.value() for param in self.sample_config_group])
        settings_group.create_dataset("sample_element_config", data=[param.value() for param in self.sample_element_config_group])
        settings_group.create_dataset("magnet_config", data=[param.value() for param in self.magnet_config_group])
        settings_group.create_dataset("inhomogeneity_config", data=[param.value() for param in self.inhomogeneity_config_group])
        settings_group.create_dataset("gradient", data=[param.value() for param in self.gradient_group])
        settings_group.create_dataset("rf", data=[param.value() for param in self.rf_group])
        settings_group.create_dataset("simulator", data=simulator)

        file_.flush()
        file_.close()

        self.path.setText(file_path)

    def openFile(self):
        """Open a dialog to select the config file to be opened."""
        file_dialog = QtGui.QFileDialog(caption="Open settings file...")
        file_dialog.setNameFilter("*.config")
        file_dialog.setAcceptMode(QtGui.QFileDialog.AcceptOpen)

        if file_dialog.exec():
            file_path = file_dialog.selectedFiles()[0]
            if file_path:
                self.open(file_path)

    def open(self, file_path):
        """Open a HDF5 settings file.

        Args:
            file_path (str): Path to a file containing the settings.

        """
        file_ = h5py.File(file_path, 'r')
        settings_group = file_.require_group("SettingsGroup")

        # Reading datasets
        sample_config_value = settings_group.require_dataset("sample_config", exact=True, shape=(10,), dtype=float).value
        sample_element_config_value = settings_group.require_dataset("sample_element_config", exact=True, shape=(9,), dtype=float).value
        magnet_config_value = settings_group.require_dataset("magnet_config", exact=True, shape=(4,), dtype=float).value
        inhomogeneity_config_value = settings_group.require_dataset("inhomogeneity_config", exact=True, shape=(6,), dtype=float).value
        gradient_value = settings_group.require_dataset("gradient", exact=True, shape=(6,), dtype=float).value
        rf_value = settings_group.require_dataset("rf", exact=True, shape=(6,), dtype=float).value
        simulator = settings_group.require_dataset("simulator", exact=True, shape=(13,), dtype=float).value

        file_.close()

        simulator_value = []
        if simulator[0] == 0:
            simulator_value += ["From Start"]
        elif simulator[0] == 1:
            simulator_value += ["Steady State"]
        if simulator[1] == 0:
            simulator_value += ["All Points"]
        elif simulator[1] == 1:
            simulator_value += ["End Points"]

        for i in range(2, len(simulator)):
            simulator_value.append(simulator[i])

        # Updating changes
        groups = [self.magnet_config_group,
                  self.sample_config_group,
                  self.sample_element_config_group,
                  self.inhomogeneity_config_group,
                  self.gradient_group, self.rf_group,
                  self.simulator_group]

        values = [magnet_config_value,
                  sample_config_value,
                  sample_element_config_value,
                  inhomogeneity_config_value,
                  gradient_value, rf_value,
                  simulator_value]

        for j in range(len(groups)):
            i = 0
            for param in groups[j]:
                param.setValue(values[j][i])
                i += 1

        self.path.setText(file_path)


if __name__ == '__main__':
    app = QtGui.QApplication([])
    window = Settings()
    window.show()
    window.resize(450, 600)
    app.exec_()
