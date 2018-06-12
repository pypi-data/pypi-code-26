#! python
# -*- coding: utf-8 -*-

"""Main window of visual simulator.

Authors:
    * Victor Hugo de Mello Pessoa <victor.pessoa@usp.br>
    * Daniel Cosmo Pizetta <daniel.pizetta@usp.br>

Since:
    2017/08/01

Todo:
    Replaning this module, divide and make it more simple.

"""

import imp
import logging
import os

import h5py
import numpy as np
import pyqtgraph as pg
from pyqtgraph import opengl as gl
from pyqtgraph import parametertree as pt
from pyqtgraph.Qt import QtCore, QtGui

from bloch.simulator import evolve
from mrsprint.gui.dlg_gradient import Ui_DialogGradient
from mrsprint.gui.mw_mrsprint import Ui_MainWindow
from mrsprint.settings import Settings
from mrsprint.simulator import create_positions, frequency_shift
from mrsprint.simulator.plot import Plot, plot_item
from mrsprint.subject.sample import Nucleus, Sample, SampleElement
from mrsprint.system.magnet import Inhomogeneity, Magnet, Resolution

_logger = logging.getLogger(__name__)


def _get_element_3d_view(position, element_size, size):
    """Return a 3D faced box item at position x, y, z.

    Args:
        position (list(int)): List of the indexes of the item.
        element_size (list(float)): List of the dimensions of the item.
        size (list(float)): List of the dimensions of the whole sample.

    Returns:
        gl.GLMeshItem(): 3D item.

    """
    x, y, z = position
    dx, dy, dz = element_size
    lx, ly, lz = size

    # translated position
    x, y, z = x * dx - lx / 2, y * dy - ly / 2, z * dz - lz / 2

    # Vertex
    v = np.array([[x, y, z],
                  [x + dx, y, z],
                  [x, y + dy, z],
                  [x + dx, y + dy, z],
                  [x, y, z + dz],
                  [x + dx, y, z + dz],
                  [x, y + dy, z + dz],
                  [x + dx, y + dy, z + dz]])

    # Faces
    f = np.array([[0, 1, 2], [1, 2, 3], [0, 1, 4],
                  [1, 4, 5], [0, 2, 4], [2, 4, 6],
                  [1, 3, 5], [3, 5, 7], [2, 3, 6],
                  [3, 6, 7], [4, 5, 6], [5, 6, 7]])

    data = gl.MeshData(vertexes=v, faces=f)
    item = gl.GLMeshItem(meshdata=data)
    item.setGLOptions(opts="translucent")

    return item


class DataEditor():
    """Class that keep data."""

    _observers = []

    def __init__(self):
        # these values provide different sizes and values to compare indexes
        self.defaultShape = [0, 0, 0]
        self.defaultSize = [0, 0, 0]
        self.defaultElementSize = [0, 0, 0]
        self.defaultValues = [0, 0, 0]   # t1, t2, rho for a sample

        self.shape = self.defaultShape                 # nx, ny, nz
        self.size = self.defaultSize                   # lx, ly, lz
        self.elementSize = self.defaultElementSize     # dx, dy, dz

        self.minimumValues = [0, 0, 0]   # min_t1, min_t2, min_rho for a sample
        self.maximumValues = [0, 0, 0]   # max_t1, max_t2, max_rho for a sample

        self.valueShape = [3]            # [3]

        self.currentValuesIndex = 0      # [t1, t2, rho] for a sample
        self.currentIndexes = [0, 0, 0]
        self.currentOpacityIndex = -1
        self.currentPath = ""

        # Data contains X, Y, Z, VALUES - its size is nx, ny, nz, nv
        self._data = np.full(self.defaultShape + self.valueShape, self.defaultValues)

    @property
    def data(self):
        """numpy.array: Get data property."""
        return self._data

    @data.setter
    def data(self, value):
        self._data = value
        self.updateObserversData()

    def getDataItem(self, x, y, z, index=None):
        """Get value in data at given index.

        Args:
            x (int): X index of the item.
            y (int): Y index of the item.
            z (int): Z index of the item.
            index (int): Index of the type of data to be returned, if no index 
                is selected, it returns the current index.

        Returns:
            float: Data value.

        """
        cur_index = self.currentValuesIndex

        if index:
            cur_index = index

        return self._data[x, y, z][cur_index]

    def setDataItem(self, x, y, z, value, index=None):
        """Set value in data at given index.

        Parameters:
            x (int): X index of the item.
            y (int): Y index of the item.
            z (int): Z index of the item.
            index (int): Index of the type of data to be returned, if no 
                index is selected, it returns the current index.

        """
        cur_index = self.currentValuesIndex

        if index:
            cur_index = index

        min_value = self.minimumValues[cur_index]
        max_value = self.maximumValues[cur_index]
        def_value = self.defaultValues[cur_index]

        new_value = def_value

        # Check value limits
        if value >= min_value and value <= max_value:
            new_value = value
        elif value < min_value:
            new_value = min_value
        elif value > max_value:
            new_value = max_value

        _logger.debug("X Y Z: %s, Value: %s, Index: %s", (x, y, z), new_value, cur_index)

        self._data[x, y, z][cur_index] = new_value

    def setValues(self, minimum_values, default_values, maximum_values):
        """
        Set the minimun, maximum and default values.

        Args:
            minimum_values (list(float)): List of minimum of each type of data.
            default_values  (list(float)): List of default of each type of data.
            maximum_values (list(float)): List of maximum of each type of data.

        """
        self.minimumValues = minimum_values
        self.defaultValues = default_values
        self.maximumValues = maximum_values

    def setDimension(self, size, shape):
        """Set value on the sample's dimensions.

        Args:
            size (list): New values of nx, ny and nz.
            shape (list): New values of sizeX, sizeY and sizeZ.

        """
        _logger.debug("Old shape: %s, New shape: %s \nOld size: %s, New size: %s",
                      self.shape, shape, self.size, size)
        self.shape = shape
        self.size = size
        self.elementSize = [size[i] / shape[i] for i in range(3)]
        self.resizeData()

    def setNX(self, value):
        """Set value on Nx.

        Args:
            value (int): New value of nx.

        """
        _logger.debug("Old NX: %s, New NX: %s ", self.shape[0], value)
        self.shape[0] = value
        self.elementSize[0] = self.size[0] / self.shape[0]
        self.resizeData()

    def setNY(self, value):
        """Set value on Ny.

        Args:
            value (int): New value of ny.

        """
        _logger.debug("Old NY: %s, New NY: %s ", self.shape[1], value)
        self.shape[1] = value
        self.elementSize[1] = self.size[1] / self.shape[1]
        self.resizeData()

    def setNZ(self, value):
        """Set value on Nz.

        Args:
            value (int): New value of nz.

        """
        _logger.debug("Old NZ: %s, New NZ: %s ", self.shape[2], value)
        self.shape[2] = value
        self.elementSize[2] = self.size[2] / self.shape[2]
        self.resizeData()

    def setSizeX(self, value):
        """Set value on SizeX.

        Args:
            value (float): New value of SizeX.

        """
        _logger.debug("Old SizeX: %s, New SizeX: %s ", self.size[0], value)
        self.size[0] = value
        self.elementSize[0] = self.size[0] / self.shape[0]
        self.updateObserversDataSize()

    def setSizeY(self, value):
        """Set value on SizeY.

        Args:
            value (float): New value of SizeY.

        """
        _logger.debug("Old SizeY: %s, New SizeY: %s ", self.size[1], value)
        self.size[1] = value
        self.elementSize[1] = self.size[1] / self.shape[1]
        self.updateObserversDataSize()

    def setSizeZ(self, value):
        """Set value on SizeZ.

        Args:
            value (float): New value of SizeZ.

        """
        _logger.debug("Old SizeZ: %s, New SizeZ: %s ", self.size[2], value)
        self.size[2] = value
        self.elementSize[2] = self.size[2] / self.shape[2]
        self.updateObserversDataSize()

    def setCurrentValuesIndex(self, value):
        """Set the value index currently selected.

        Args:
            value (int): New value of index selected.

        """
        _logger.debug("Old value index: %s, New value index: %s ",
                      self.currentValuesIndex, value)
        self.currentValuesIndex = value
        self.updateObserversIndex()

    def setCurrentOpacityIndex(self, value):
        """Select the type of data responsible for adjust the opacity.

        Args:
            value (int): New value of opacity index

        """
        _logger.debug("Old opacity index: %s, New opacity index: %s ",
                      self.currentValuesIndex, value)
        self.currentOpacityIndex = value
        self.updateObserversIndex()

    def resizeData(self):
        """Resize the matrix containing data using shape."""
        data_old = self.data.copy()
        new_shape = self.shape

        for index, _ in enumerate(self.defaultElementSize):
            self.defaultElementSize[index] = self.size[index] / self.shape[index]

        self.data = np.full(new_shape + self.valueShape, self.defaultValues)

        _logger.debug("Old shape: %s, New shape: %s ", data_old.shape, self.data.shape)

        for i in range(min(data_old.shape[0], self.data.shape[0])):
            for j in range(min(data_old.shape[1], self.data.shape[1])):
                for k in range(min(data_old.shape[2], self.data.shape[2])):
                    self.data[i, j, k] = data_old[i, j, k]

        self.updateObserversDataSize()

    @classmethod
    def registerObserver(cls, observer):
        """Register observers to be updated.

        Args:
            observer (object): Object to be registered.
        """
        if observer not in cls._observers:
            cls._observers.append(observer)

    @classmethod
    def updateObserversIndex(cls):
        """Update the observers index."""
        for observer in cls._observers:
            try:
                observer.updateObserverIndex()
            except Exception as e:
                _logger.warning("Could not update observer: %s!", e)
            else:
                _logger.debug("Number of observers updated: %s", len(cls._observers))

    @classmethod
    def updateObserversData(cls):
        """Update the observers data."""
        for observer in cls._observers:
            try:
                observer.updateObserverData()
            except Exception as e:
                _logger.warning("Could not update observer: %s!", e)
            else:
                _logger.debug("Number of observers updated: %s", len(cls._observers))

    @classmethod
    def updateObserversDataSize(cls):
        """Update the observers data size - must recreate."""
        for observer in cls._observers:
            try:
                observer.updateObserverDataSize()
            except Exception as e:
                _logger.warning("Could not update observer: %s!", e)
            else:
                _logger.debug("Number of observers updated: %s", len(cls._observers))


class MainWindow(QtGui.QMainWindow):
    """Main window."""

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        # Useful definitions
        red = [0.4, 0.2, 0.2]
        green = [0.2, 0.4, 0.2]
        blue = [0.2, 0.2, 0.4]

        self.colors = [red, green, blue]

        self.tables2DEditor = [self.ui.tableWidget2DEditorXY,
                               self.ui.tableWidget2DEditorXZ,
                               self.ui.tableWidget2DEditorYZ]

        self.updateMethods2DEditor = [self.updateDataFromTable2DEditor,
                                      self.updateDataFromTable2DEditor,
                                      self.updateDataFromTable2DEditor]

        self.sliders2DEditor = [self.ui.horizontalSlider2DEditorZIndex,
                                self.ui.horizontalSlider2DEditorYIndex,
                                self.ui.horizontalSlider2DEditorXIndex]

        self.spinBoxes2DEditor = [self.ui.spinBox2DEditorZIndex,
                                  self.ui.spinBox2DEditorYIndex,
                                  self.ui.spinBox2DEditorXIndex]

        self.currentExtension = ""
        self.filepath = {"Sample": "", "System": "", "Sequence": "", "Config": ""}
        self.fileChanged = False

        self.parameterTree = pt.ParameterTree(self.ui.dockWidgetParameters)
        self.ui.dockWidgetParameters.setWidget(self.parameterTree)

        self.dataEditor = DataEditor()
        self.dataEditor.registerObserver(self)

        # TODO: put this in a function
        self.pathIni = os.path.join(os.path.abspath(os.path.dirname(__file__)) + "/file.ini")
        if os.path.isfile(self.pathIni):
            file_ini = open(self.pathIni, "r")
            lines = file_ini.read().split("\n")

            for line in lines:
                split = line.split("=")
                if split[0] == "CONFIG_PATH":
                    self.filepath["Config"] = split[1]
                elif split[0] == "SAMPLE_PATH":
                    self.filepath["Sample"] = split[1]
                elif split[0] == "SYSTEM_PATH":
                    self.filepath["System"] = split[1]
                elif split[0] == "SEQUENCE_PATH":
                    self.filepath["Sequence"] = split[1]

        else:
            self.filepath["Config"] = os.path.join(os.path.abspath(os.path.dirname(__file__)) + "/default.config")

        # Settings
        self.settings = Settings(self, QtCore.Qt.Dialog)
        self.settings.setWindowModality(QtCore.Qt.WindowModal)
        self.settings.resize(450, 600)

        self.settings.sample_config_group.sigTreeStateChanged.connect(self.sampleSettingsChanges)
        self.settings.sample_element_config_group.sigTreeStateChanged.connect(self.sampleSettingsChanges)
        self.settings.magnet_config_group.sigTreeStateChanged.connect(self.systemSettingsChanges)
        self.settings.inhomogeneity_config_group.sigTreeStateChanged.connect(self.systemSettingsChanges)
        self.settings.simulator_group.sigTreeStateChanged.connect(self.simulatorSettingsChanges)
        self.settings.rf_group.sigTreeStateChanged.connect(self.simulatorSettingsChanges)
        self.settings.gradient_group.sigTreeStateChanged.connect(self.simulatorSettingsChanges)
        self.settings.path.textChanged.connect(self.setSettingsPath)

        self.ui.actionConfigurationPreferences.triggered.connect(lambda: self.settings.show())

        # File
        self.ui.actionFileNew.triggered.connect(self.fileNew)
        self.ui.actionFileOpen.triggered.connect(self.fileOpen)
        self.ui.actionFileSave.triggered.connect(self.fileSave)
        self.ui.actionFileSaveAs.triggered.connect(self.fileSaveAs)
        self.ui.actionFileClose.triggered.connect(self.fileClose)
        self.ui.actionQuit.triggered.connect(self.quit)

        self.ui.actionFileSequenceOpen.triggered.connect(self.fileOpen)

        # Change tab (focus) when tabified
        self.ui.action2DEditorXY.triggered.connect(self.ui.dockWidget2DEditorXY.raise_)
        self.ui.action2DEditorXZ.triggered.connect(self.ui.dockWidget2DEditorXZ.raise_)
        self.ui.action2DEditorYZ.triggered.connect(self.ui.dockWidget2DEditorYZ.raise_)
        self.ui.action2DEditorXYZ.triggered.connect(self.tabify2DEditor)

        # Background, color and gradient
        self.ui.action2DEditorGradient.triggered.connect(self.gradient2DEditor)
        self.ui.action2DEditorColor.triggered.connect(self.updateTableFromData2DEditor)

        self.ui.tableWidget2DEditorXZ.itemChanged.connect(self.updateDataFromTable2DEditor)
        self.ui.tableWidget2DEditorYZ.itemChanged.connect(self.updateDataFromTable2DEditor)
        self.ui.tableWidget2DEditorXY.itemChanged.connect(self.updateDataFromTable2DEditor)

        self.ui.tableWidget2DEditorXY.itemSelectionChanged.connect(self.enableGradient2DEditor)
        self.ui.tableWidget2DEditorXZ.itemSelectionChanged.connect(self.enableGradient2DEditor)
        self.ui.tableWidget2DEditorYZ.itemSelectionChanged.connect(self.enableGradient2DEditor)

        self.ui.tableWidget2DEditorXY.itemSelectionChanged.connect(self.clearSelection2DEditor)
        self.ui.tableWidget2DEditorXZ.itemSelectionChanged.connect(self.clearSelection2DEditor)
        self.ui.tableWidget2DEditorYZ.itemSelectionChanged.connect(self.clearSelection2DEditor)

        self.ui.horizontalSlider2DEditorXIndex.valueChanged.connect(self.updateTableFromData2DEditor)
        self.ui.horizontalSlider2DEditorYIndex.valueChanged.connect(self.updateTableFromData2DEditor)
        self.ui.horizontalSlider2DEditorZIndex.valueChanged.connect(self.updateTableFromData2DEditor)

        # Context
        self.ui.actionContextSample.triggered.connect(self.loadSampleParameters)
        self.ui.actionContextSystem.triggered.connect(self.loadSystemParameters)
        self.ui.actionContextSequence.triggered.connect(self.loadSequenceParameters)
        self.ui.actionContextSimulator.triggered.connect(self.loadSimulatorParameters)
        self.ui.actionContextProcessing.triggered.connect(self.loadProcessingParameters)

        self.removeToolBar(self.ui.toolBarContext)
        self.addToolBar(QtCore.Qt.LeftToolBarArea, self.ui.toolBarContext)
        self.ui.toolBarContext.show()

        # Parameters
        self.sample = None
        self.sampleElement = None
        self.inhomogeneity = None
        self.resolution = None
        self.nucleus = None
        self.magnet = None
        self.sequenceExample = None
        self.plot = None

        # Sample
        self.ui.actionSampleElementT1.triggered.connect(lambda: self.dataEditor.setCurrentValuesIndex(0))
        self.ui.actionSampleElementT2.triggered.connect(lambda: self.dataEditor.setCurrentValuesIndex(1))
        self.ui.actionSampleElementRho.triggered.connect(lambda: self.dataEditor.setCurrentValuesIndex(2))

        # Field Inhomogeneity
        self.ui.actionFieldInhomogeneityB0X.triggered.connect(lambda: self.dataEditor.setCurrentValuesIndex(0))
        self.ui.actionFieldInhomogeneityB0Y.triggered.connect(lambda: self.dataEditor.setCurrentValuesIndex(1))
        self.ui.actionFieldInhomogeneityB0Z.triggered.connect(lambda: self.dataEditor.setCurrentValuesIndex(2))

        # Simulator
        self.ui.actionSimulatorRun.triggered.connect(self.simulationRun)
        self.ui.actionSimulatorCalculate.triggered.connect(self.simulate)

        # Main dockWidget
        self.dockWidgetMain = QtGui.QDockWidget()
        self.dockWidgetMain.setFeatures(QtGui.QDockWidget.DockWidgetFloatable)
        self.setCentralWidget(self.dockWidgetMain)

        # Side dockWidget
        self.dockWidgetSide = QtGui.QDockWidget()
        self.dockWidgetSide.setFeatures(QtGui.QDockWidget.DockWidgetFloatable)
        self.addDockWidget(QtCore.Qt.DockWidgetArea(2), self.dockWidgetSide)

        # Graphics View
        self.graphicsSequence = None
        self.graphicsMagnetization = None
        self.graphicsIFT = None

        # 3D View
        self.view3DCameraLayout = QtGui.QWidget(self.dockWidgetMain)
        self.view3D = None
        self.spinView3D = None

        # Image View
        self.kSpaceView = None

        # Camera
        self.ui.action3DViewCameraXYZ.triggered.connect(lambda: self.view3D.setCameraPosition(elevation=30, azimuth=45))
        self.ui.action3DViewCameraXY.triggered.connect(lambda: self.view3D.setCameraPosition(elevation=270, azimuth=270))
        self.ui.action3DViewCameraYZ.triggered.connect(lambda: self.view3D.setCameraPosition(elevation=180, azimuth=0))
        self.ui.action3DViewCameraXZ.triggered.connect(lambda: self.view3D.setCameraPosition(elevation=180, azimuth=270))

        # Axis
        self.ui.action3DViewXYZAxis.triggered.connect(self.showAxis3DView)

        # Background and color
        self.ui.action3DViewInvertBackground.triggered.connect(self.invertBackground3DView)
        self.ui.action3DViewColor.triggered.connect(self.updateViewFromData3DView)

        # Action groups
        sample_action_group = QtGui.QActionGroup(self)
        sample_action_group.addAction(self.ui.actionSampleElementRho)
        sample_action_group.addAction(self.ui.actionSampleElementT1)
        sample_action_group.addAction(self.ui.actionSampleElementT2)
        sample_action_group.setExclusive(True)

        system_action_group = QtGui.QActionGroup(self)
        system_action_group.addAction(self.ui.actionFieldInhomogeneityB0X)
        system_action_group.addAction(self.ui.actionFieldInhomogeneityB0Y)
        system_action_group.addAction(self.ui.actionFieldInhomogeneityB0Z)
        system_action_group.setExclusive(True)

        context_action_group = QtGui.QActionGroup(self)
        context_action_group.addAction(self.ui.actionContextSample)
        context_action_group.addAction(self.ui.actionContextSystem)
        context_action_group.addAction(self.ui.actionContextSequence)
        context_action_group.addAction(self.ui.actionContextSimulator)
        context_action_group.addAction(self.ui.actionContextProcessing)
        context_action_group.setExclusive(True)

        plane_action_group = QtGui.QActionGroup(self)
        plane_action_group.addAction(self.ui.action2DEditorXY)
        plane_action_group.addAction(self.ui.action2DEditorXZ)
        plane_action_group.addAction(self.ui.action2DEditorYZ)
        plane_action_group.setExclusive(True)
        plane_action_group.setEnabled(False)

        self.ui.spinBox2DEditorXIndex.valueChanged.connect(self.translateGrid3DView)
        self.ui.spinBox2DEditorYIndex.valueChanged.connect(self.translateGrid3DView)
        self.ui.spinBox2DEditorZIndex.valueChanged.connect(self.translateGrid3DView)

        self.ui.action2DEditorGradient.setEnabled(False)
        self.ui.action2DEditorXY.setChecked(True)
        self.ui.actionContextSample.setChecked(True)

        self.ui.action2DEditorXYZ.triggered.connect(plane_action_group.setDisabled)
        self.ui.actionSampleElementAll.triggered.connect(sample_action_group.setDisabled)
        self.ui.actionFieldInhomogeneityAll.triggered.connect(system_action_group.setDisabled)
        self.invertBackground2DEditor(invert=True)

        self.loadSettings()
        self.loadSystemParameters()
        self.loadSequenceParameters()
        self.loadSampleParameters()

        self.updateObserverData()
        self.updateObserverIndex()

    def updateObserverDataSize(self):
        """Reread data and apply updates, maybe need some rebuild."""
        self.resizeTable2DEditor()
        self.create3DView()
        self.ui.horizontalSlider2DEditorXIndex.blockSignals(True)
        self.ui.horizontalSlider2DEditorXIndex.setValue(0)
        self.ui.horizontalSlider2DEditorXIndex.blockSignals(False)
        self.ui.horizontalSlider2DEditorYIndex.blockSignals(True)
        self.ui.horizontalSlider2DEditorYIndex.setValue(0)
        self.ui.horizontalSlider2DEditorYIndex.blockSignals(False)
        self.ui.horizontalSlider2DEditorZIndex.blockSignals(True)
        self.ui.horizontalSlider2DEditorZIndex.setValue(0)
        self.ui.horizontalSlider2DEditorZIndex.blockSignals(False)
        return 0

    def updateObserverData(self):
        """Reread data and apply updates."""
        self.updateTableFromData2DEditor()
        self.updateViewFromData3DView()
        return 0

    def updateObserverIndex(self):
        """Reread indexes and apply updates, does not need recreated anything."""
        self.updateTableFromData2DEditor()
        self.updateViewFromData3DView()
        return 0

    def setSettingsPath(self):
        self.filepath["Config"] = self.settings.path.text()

    def loadSettings(self):
        """Load all the config parameters needed by the software."""
        self.settings.open(self.filepath["Config"])

        self.magnetSize = [param.value() for param in self.settings.magnet_config_group]
        del self.magnetSize[0]

    def loadSampleParameters(self):
        """Load sample parameters and connect signals.

        This method should exist for each type of context that could be edited
        in the 2D editor and 3D view. Ex. loadSystemParameters.

        It should be responsible to load values from parameter tree, connect
        signals - to respective own actions, and set data.

        To keep it isolated, it should set data, and when data is changed,
        data triggers the GUI update. And the reverse mode.

        """
        # Sample element
        self.sampleElement = SampleElement(self.settings.sample_element_config_group)

        self.sampleElement.t1.sigValueChanged.connect(lambda: self.updateSelectedCells(self.sampleElement.t1.value(), 0))
        self.sampleElement.t2.sigValueChanged.connect(lambda: self.updateSelectedCells(self.sampleElement.t2.value(), 1))
        self.sampleElement.rho.sigValueChanged.connect(lambda: self.updateSelectedCells(self.sampleElement.rho.value(), 2))

        self.ui.actionSampleElementT1.setChecked(True)
        self.dataEditor.setCurrentValuesIndex(0)

        self.parameterTree.clear()
        self.parameterTree.addParameters(self.sampleElement)

        # Sample
        self.sample = Sample(self.settings.sample_config_group)

        self.sample.Nx.sigValueChanged.connect(lambda: self.dataEditor.setNX(self.sample.Nx.value()))
        self.sample.Ny.sigValueChanged.connect(lambda: self.dataEditor.setNY(self.sample.Ny.value()))
        self.sample.Nz.sigValueChanged.connect(lambda: self.dataEditor.setNZ(self.sample.Nz.value()))

        self.sample.SizeX.sigValueChanged.connect(lambda: self.dataEditor.setSizeX(self.sample.SizeX.value()))
        self.sample.SizeY.sigValueChanged.connect(lambda: self.dataEditor.setSizeY(self.sample.SizeY.value()))
        self.sample.SizeZ.sigValueChanged.connect(lambda: self.dataEditor.setSizeZ(self.sample.SizeZ.value()))

        self.parameterTree.addParameters(self.sample)

        # Hiding/Unhiding and Enabling/Desabling widgets
        self.dockWidgetMain.setWindowTitle("Sample 3D View")
        self.dockWidgetSide.hide()
        self.ui.dockWidgetParameters.show()
        self.ui.dockWidget2DEditorXY.show()
        self.ui.dockWidget2DEditorXZ.show()
        self.ui.dockWidget2DEditorYZ.show()

        self.ui.toolBarSampleElement.show()
        self.ui.toolBarFieldInhomogeneity.hide()
        self.ui.toolBarSimulator.hide()

        self.ui.toolBar2DEditor.setEnabled(True)
        self.ui.toolBar3DViewCamera.setEnabled(True)
        self.ui.toolBar3DView.setEnabled(True)
        self.ui.toolBarFile.show()
        self.ui.toolBarFileSequence.hide()

        max_t1 = self.settings.sample_element_config_group.maxT1.value()
        def_t1 = self.settings.sample_element_config_group.t1.value()
        min_t1 = self.settings.sample_element_config_group.minT1.value()

        max_t2 = self.settings.sample_element_config_group.maxT2.value()
        def_t2 = self.settings.sample_element_config_group.t2.value()
        min_t2 = self.settings.sample_element_config_group.minT2.value()

        max_rho = self.settings.sample_element_config_group.maxRho.value()
        def_rho = self.settings.sample_element_config_group.rho.value()
        min_rho = 0.

        self.currentExtension = ".spl"
        default_shape = [self.sample.Nx.value(), self.sample.Ny.value(), self.sample.Nz.value()]
        default_size = [self.sample.SizeX.value(), self.sample.SizeY.value(), self.sample.SizeZ.value()]
        self.dataEditor.setDimension(default_size, default_shape)
        self.dataEditor.currentOpacityIndex = 2
        self.dataEditor.setValues([min_t1, min_t2, min_rho],
                                  [def_t1, def_t2, def_rho],
                                  [max_t1, max_t2, max_rho])

        self.dataEditor.data = np.full(self.dataEditor.shape + [3], self.dataEditor.defaultValues)

        if self.filepath["Sample"]:
            self.openSample(self.filepath["Sample"])

        self.create3DView()

    def loadSystemParameters(self):
        """Load system config parameters and connect signals."""
        # Hiding/Unhiding and Enabling/Desabling widgets
        self.dockWidgetMain.setWindowTitle("Magnet 3D View")
        self.dockWidgetSide.hide()
        self.ui.dockWidgetParameters.show()
        self.ui.dockWidget2DEditorXY.show()
        self.ui.dockWidget2DEditorXZ.show()
        self.ui.dockWidget2DEditorYZ.show()

        self.ui.toolBarSampleElement.hide()
        self.ui.toolBarFieldInhomogeneity.show()
        self.ui.toolBarSimulator.hide()

        self.ui.toolBar2DEditor.setEnabled(True)
        self.ui.toolBar3DViewCamera.setEnabled(True)
        self.ui.toolBar3DView.setEnabled(True)
        self.ui.toolBarFile.show()
        self.ui.toolBarFileSequence.hide()

        # Field Inhomogeneity
        self.inhomogeneity = Inhomogeneity(self.settings.inhomogeneity_config_group)

        self.ui.actionFieldInhomogeneityB0X.setChecked(True)
        self.dataEditor.setCurrentValuesIndex(0)

        self.parameterTree.clear()
        self.parameterTree.addParameters(self.inhomogeneity)

        # Resolution
        self.resolution = Resolution()

        self.resolution.N.sigValueChanged.connect(lambda: self.dataEditor.setDimension(self.magnetSize, [self.resolution.N.value() for i in range(3)]))

        self.parameterTree.addParameters(self.resolution)

        # Nucleus
        self.nucleus = Nucleus()
        self.nucleus.nucleus.sigValueChanged.connect(self.nucleus.updateGamma)
        self.parameterTree.addParameters(self.nucleus)

        # Magnet
        self.magnet = Magnet(self.settings.magnet_config_group)
        self.magnetSize = [param.value() for param in self.settings.magnet_config_group]
        del self.magnetSize[0]

        self.nucleus.gamma.sigValueChanged.connect(
            lambda: self.magnet.carrierFrequency.setValue(
                self.magnet.magneticStrength.value() * self.nucleus.gamma.value()))
        self.magnet.magneticStrength.sigValueChanged.connect(
            lambda: self.magnet.carrierFrequency.setValue(
                self.magnet.magneticStrength.value() * self.nucleus.gamma.value()))

        self.parameterTree.addParameters(self.magnet)

        max_b0x = self.settings.inhomogeneity_config_group.limitB0x.value()
        def_b0x = self.settings.inhomogeneity_config_group.B0x.value()
        min_b0x = - max_b0x

        max_b0y = self.settings.inhomogeneity_config_group.limitB0y.value()
        def_b0y = self.settings.inhomogeneity_config_group.B0z.value()
        min_b0y = - max_b0y

        max_b0z = self.settings.inhomogeneity_config_group.limitB0z.value()
        def_b0z = self.settings.inhomogeneity_config_group.B0z.value()
        min_b0z = - max_b0z

        self.currentExtension = ".stm"
        self.dataEditor.setDimension(self.magnetSize, [2, 2, 2])
        self.dataEditor.currentOpacityIndex = -1
        self.dataEditor.setValues([min_b0x, min_b0y, min_b0z],
                                  [def_b0x, def_b0y, def_b0z],
                                  [max_b0x, max_b0y, max_b0z])

        self.dataEditor.data = np.full(self.dataEditor.shape + [3], self.dataEditor.defaultValues)

        if self.filepath["System"]:
            self.openSystem(self.filepath["System"])
        self.create3DView()

    def loadSequenceParameters(self):
        """Load sequence parameters and connect signals."""
        # Hiding/Unhiding and Enabling/Desabling widgets
        self.dockWidgetMain.setWindowTitle("RF and Gradient")
        self.dockWidgetSide.hide()
        self.ui.dockWidget2DEditorXY.hide()
        self.ui.dockWidget2DEditorXZ.hide()
        self.ui.dockWidget2DEditorYZ.hide()

        self.ui.dockWidgetParameters.show()

        self.ui.toolBarSampleElement.hide()
        self.ui.toolBarFieldInhomogeneity.hide()
        self.ui.toolBarSimulator.hide()

        self.ui.toolBar2DEditor.setEnabled(False)
        self.ui.toolBar3DViewCamera.setEnabled(False)
        self.ui.toolBar3DView.setEnabled(False)
        self.ui.toolBarFile.hide()
        self.ui.toolBarFileSequence.show()

        self.parameterTree.clear()
        if self.sequenceExample is not None:
            self.parameterTree.addParameters(self.sequenceExample)

        self.dockWidgetMain.setWidget(self.graphicsSequence)

        self.currentExtension = ".py"
        if self.filepath["Sequence"]:
            self.openSequence(self.filepath["Sequence"])

    def loadSimulatorParameters(self):
        """Load simulator parameters and connect signals."""
        # Hiding/Unhiding and Enabling/Desabling widgets
        self.dockWidgetSide.show()
        self.ui.dockWidget2DEditorXY.hide()
        self.ui.dockWidget2DEditorXZ.hide()
        self.ui.dockWidget2DEditorYZ.hide()

        self.ui.dockWidgetParameters.hide()

        self.ui.toolBarSampleElement.hide()
        self.ui.toolBarFieldInhomogeneity.hide()
        self.ui.toolBarSimulator.show()

        self.ui.toolBar2DEditor.setEnabled(False)
        self.ui.toolBar3DViewCamera.setEnabled(False)
        self.ui.toolBar3DView.setEnabled(False)
        self.ui.toolBarFile.hide()
        self.ui.toolBarFileSequence.hide()

        self.spinView3D = gl.GLViewWidget()
        self.graphicsMagnetization = pg.GraphicsWindow()

        self.dockWidgetMain.setWidget(self.spinView3D)
        self.dockWidgetSide.setWidget(self.graphicsMagnetization)

        self.dockWidgetMain.setWindowTitle("Spin 3D View")
        self.dockWidgetSide.setWindowTitle("Magnetization")

        self.ui.actionSimulatorPlay.setEnabled(False)
        self.ui.actionSimulatorPause.setEnabled(False)
        self.ui.actionSimulatorStop.setEnabled(False)
        self.ui.actionSimulatorRun.setEnabled(False)

        simulator_ready = True
        missing_contexts = []
        for context in self.filepath:
            if(not self.filepath[context]):
                simulator_ready = False
                missing_contexts.append(context)

        self.ui.actionSimulatorCalculate.setEnabled(simulator_ready)

        if not simulator_ready:
            title = "Simulator context"
            message = "There is no saved file from " + missing_contexts[0]
            for i in range(1, len(missing_contexts) - 1):
                message += ", " + missing_contexts[i]

            if(len(missing_contexts) > 1):
                message += " and " + missing_contexts[len(missing_contexts) - 1]
                message += " contexts.\nThese files are needed to start a simulation."
            else:
                message += " context.\nThis file is needed to start a simulation."

            message_box = QtGui.QMessageBox(QtGui.QMessageBox.Warning, title, message)
            message_box.exec()

    def loadProcessingParameters(self):
        """Load processing parameters and connect signals."""
        # Hiding/Unhiding and Enabling/Desabling widgets
        self.dockWidgetSide.hide()
        self.ui.dockWidget2DEditorXY.hide()
        self.ui.dockWidget2DEditorXZ.hide()
        self.ui.dockWidget2DEditorYZ.hide()

        self.ui.dockWidgetParameters.hide()

        self.ui.toolBarSampleElement.hide()
        self.ui.toolBarFieldInhomogeneity.hide()
        self.ui.toolBarSimulator.hide()

        self.ui.toolBar2DEditor.setEnabled(False)
        self.ui.toolBar3DViewCamera.setEnabled(False)
        self.ui.toolBar3DView.setEnabled(False)
        self.ui.toolBarFile.hide()
        self.ui.toolBarFileSequence.hide()

        self.dockWidgetMain.setWindowTitle("Inverse Fourier Transform")
        self.graphicsIFT = pg.GraphicsWindow()
        self.dockWidgetMain.setWidget(self.graphicsIFT)

        if self.plot is None :
            # Message error
            title = "Processing context"
            message = "There is no simulation of experiment by now.\nPlease select the 'Simulator context' and calculate a new simulation."

            message_box = QtGui.QMessageBox(QtGui.QMessageBox.Warning, title, message)
            message_box.exec()
        else:
            # Complex ifft
            # gamma Grad t = 2 pi k
            # rad/(G*s) * G/cm * s = rad * 1/cm
            # k = 1/z
            # z = 1/k
            # k = gamma grad t / 2 pi
            # k = 26752.219*20/(2*np.pi)

            read = self.sequenceExample.read
            G_x = max(self.sequenceExample.gr[0])
            n = len(read)
            dt = self.sequenceExample.dt

            freq = np.arange(0, n) * 2 * np.pi / (26752.219 * G_x * dt * n)
            # freq = np.fft.fftfreq(n, dt)*2*np.pi/(26752.219*G_x)
            data_ifft_abs = np.absolute(np.fft.ifft(self.plot.reduced_mxy[read[0]:read[-1] + 1]))
            self.graphicsIFT.addPlot(y=data_ifft_abs, x=freq)

    def sampleSettingsChanges(self):
        """Reload sample parameters."""
        if self.ui.actionContextSample.isChecked():
            self.loadSampleParameters()

    def systemSettingsChanges(self):
        """Reload system parameters."""
        if self.ui.actionContextSystem.isChecked():
            self.loadSystemParameters()

    def simulatorSettingsChanges(self):
        """Reload simulator parameters."""
        if self.filepath["Sequence"]:
            imp.load_source("sequence", self.filepath["Sequence"])
            import sequence
            self.sequenceExample = sequence.SequenceExample(self.settings, self.nucleus)
        if self.ui.actionContextSequence.isChecked():
            self.loadSequenceParameters()

    # 2D Editor ----------------------------------------------------------------------------

    def setIndexLimits2DEditor(self, nx, ny, nz):
        """Set index limits for 2D editor.

        nx (int): Shape of data in the x dimension
        ny (int): Shape of data in the y dimension
        nz (int): Shape of data in the z dimension

        """
        # X index
        self.ui.spinBox2DEditorXIndex.setMaximum(nx - 1)
        self.ui.spinBox2DEditorXIndex.setMinimum(0)

        self.ui.horizontalSlider2DEditorXIndex.setMaximum(ny - 1)
        self.ui.horizontalSlider2DEditorXIndex.setMinimum(0)
        # Y index
        self.ui.spinBox2DEditorYIndex.setMaximum(ny - 1)
        self.ui.spinBox2DEditorYIndex.setMinimum(0)

        self.ui.horizontalSlider2DEditorYIndex.setMaximum(ny - 1)
        self.ui.horizontalSlider2DEditorYIndex.setMinimum(0)
        # Z index
        self.ui.spinBox2DEditorZIndex.setMaximum(nz)
        self.ui.spinBox2DEditorZIndex.setMinimum(0)

        self.ui.horizontalSlider2DEditorZIndex.setMaximum(nz - 1)
        self.ui.horizontalSlider2DEditorZIndex.setMinimum(0)

    def resizeTable2DEditor(self):
        """Change the size of the tableWidgets whenever a row/column is added/removed."""
        nx, ny, nz = self.dataEditor.shape

        _logger.debug("Shape: %s", (nx, ny, nz))

        # In the order tables are listed
        rows_size = [ny, nz, nz]
        cols_size = [nx, nx, ny]
        page_size = [nz, ny, nx]

        row_label = ["Y", "Z", "Z"]
        column_label = ["X", "X", "Y"]

        # Run over 3 tables
        for index in range(3):

            row_size_old = self.tables2DEditor[index].rowCount()
            column_size_old = self.tables2DEditor[index].columnCount()

            # _logger.debug("Table index: %s Row count old:%s Column count old: %s ", index, row_size_old, column_size_old)

            self.tables2DEditor[index].setColumnCount(cols_size[index])
            self.tables2DEditor[index].setRowCount(rows_size[index])

            self.sliders2DEditor[index].setMinimum(0)
            self.spinBoxes2DEditor[index].setMinimum(0)

            self.sliders2DEditor[index].setMaximum(page_size[index] - 1)
            self.spinBoxes2DEditor[index].setMaximum(page_size[index] - 1)

            # Set row labels
            row_labels = [row_label[index] + str(i) for i in range(rows_size[index])]
            self.tables2DEditor[index].setVerticalHeaderLabels(row_labels)

            # Set column labels
            column_labels = [column_label[index] + str(i) for i in range(cols_size[index])]
            self.tables2DEditor[index].setHorizontalHeaderLabels(column_labels)

            self.tables2DEditor[index].blockSignals(True)

            # Process rows
            if rows_size[index] > row_size_old:
                for i in range(row_size_old, rows_size[index]):
                    for j in range(self.tables2DEditor[index].columnCount()):
                        item = QtGui.QTableWidgetItem()
                        self.tables2DEditor[index].setItem(i, j, item)

            elif rows_size[index] < row_size_old:
                for i in range(row_size_old, rows_size[index]):
                    for j in range(self.tables2DEditor[index].columnCount()):
                        self.tables2DEditor[index].takeItem(i, j)

            # Process columns
            if cols_size[index] > column_size_old:
                for i in range(self.tables2DEditor[index].rowCount()):
                    for j in range(column_size_old, cols_size[index]):
                        item = QtGui.QTableWidgetItem()
                        self.tables2DEditor[index].setItem(i, j, item)

            elif cols_size[index] < column_size_old:
                for i in range(self.tables2DEditor[index].rowCount()):
                    for j in range(column_size_old, cols_size[index]):
                        self.tables2DEditor[index].takeItem(i, j)

            # row_size_new = self.tables2DEditor[index].rowCount()
            # column_size_new = self.tables2DEditor[index].columnCount()

            # _logger.debug("Table index: %s Row count new:%s Column count new: %s  >", index, row_size_new, column_size_new)

            self.tables2DEditor[index].blockSignals(False)

        self.updateTableFromData2DEditor()

    def clearSelection2DEditor(self, all_tables=False):
        """Clear selection of all 2D editor tables.

        Args:
            all_tables (bool): Informs if all tables are shown or not.

        """
        if not self.ui.tableWidget2DEditorXY.hasFocus() or all_tables:
            self.ui.tableWidget2DEditorXY.clearSelection()
        if not self.ui.tableWidget2DEditorXZ.hasFocus() or all_tables:
            self.ui.tableWidget2DEditorXZ.clearSelection()
        if not self.ui.tableWidget2DEditorYZ.hasFocus() or all_tables:
            self.ui.tableWidget2DEditorYZ.clearSelection()

    def updateTableFromData2DEditor(self):
        """Update items of all 2D editor using 3d-array data and set color.

        This method is called when the data shape is changed or when 
        the plane index is changed. Also, when the data index is changed.

        """
        # Get plane indexes - visual information only
        x_index = self.ui.horizontalSlider2DEditorXIndex.value()
        y_index = self.ui.horizontalSlider2DEditorYIndex.value()
        z_index = self.ui.horizontalSlider2DEditorZIndex.value()

        # Get data shape
        nx, ny, nz = self.dataEditor.shape

        _logger.debug("Shape: %s, Plane indexes: %s ", (nx, ny, nz), (x_index, y_index, z_index))

        # Prevent multiple signals
        self.ui.tableWidget2DEditorXY.blockSignals(True)
        self.ui.tableWidget2DEditorXZ.blockSignals(True)
        self.ui.tableWidget2DEditorYZ.blockSignals(True)

        min_value = self.dataEditor.minimumValues[self.dataEditor.currentValuesIndex]
        max_value = self.dataEditor.maximumValues[self.dataEditor.currentValuesIndex]
        max_opacity = 1
        if self.dataEditor.currentOpacityIndex != -1:
            max_opacity = self.dataEditor.maximumValues[self.dataEditor.currentOpacityIndex]

        rgb = self.colors[self.dataEditor.currentValuesIndex]

        def color_settings(rgb, value, opacity):
            """Return background color to color table item.

            Args:
                rgb (list(float)): List of minimum values of each color in rgb ([r, g, b] from 0. to 1.).
                value (float): Value of data (from 0. to 1.).
                opacity (float): Value of opacity (from 0. to 1.).

            Returns:
                QtGui.QBrush: Color.

            """
            color = QtGui.QBrush(QtGui.QColor(int(255 * (0.6 * value)),
                                              int(255 * (0.6 * value)),
                                              int(255 * (0.6 * value)),
                                              int(255 * .5 * opacity)), QtCore.Qt.SolidPattern)

            if self.ui.action2DEditorColor.isChecked():
                color = QtGui.QBrush(QtGui.QColor(int(255 * (rgb[0] + 0.6 * value)),
                                                  int(255 * (rgb[1] + 0.6 * value)),
                                                  int(255 * (rgb[2] + 0.6 * value)),
                                                  int(255 * .5 * opacity)), QtCore.Qt.SolidPattern)
            return color

        for i in range(nx):
            for j in range(ny):
                # Changes on plane XY
                xy_value = self.dataEditor.getDataItem(i, j, z_index)
                xy_norm_value = (max_value - xy_value) / (max_value - min_value)
                opacity = 1.
                if self.dataEditor.currentOpacityIndex != -1:
                    opacity = self.dataEditor.getDataItem(i, j, z_index, self.dataEditor.currentOpacityIndex) / max_opacity
                self.ui.tableWidget2DEditorXY.item(j, i).setText(str(xy_value))
                self.ui.tableWidget2DEditorXY.item(j, i).setBackground(color_settings(rgb, xy_norm_value, opacity))
                for k in range(nz):
                    # Changes on plane XZ
                    xz_value = self.dataEditor.getDataItem(i, y_index, k)
                    xz_norm_value = (max_value - xz_value) / (max_value - min_value)
                    opacity = 1.
                    if self.dataEditor.currentOpacityIndex != -1:
                        opacity = self.dataEditor.getDataItem(i, y_index, k, self.dataEditor.currentOpacityIndex) / max_opacity
                    self.ui.tableWidget2DEditorXZ.item(k, i).setText(str(xz_value))
                    self.ui.tableWidget2DEditorXZ.item(k, i).setBackground(color_settings(rgb, xz_norm_value, opacity))
                    # Changes on plane YZ
                    yz_value = self.dataEditor.getDataItem(x_index, j, k)
                    yz_norm_value = (max_value - yz_value) / (max_value - min_value)
                    opacity = 1.
                    if self.dataEditor.currentOpacityIndex != -1:
                        opacity = self.dataEditor.getDataItem(x_index, j, k, self.dataEditor.currentOpacityIndex) / max_opacity
                    self.ui.tableWidget2DEditorYZ.item(k, j).setText(str(yz_value))
                    self.ui.tableWidget2DEditorYZ.item(k, j).setBackground(color_settings(rgb, yz_norm_value, opacity))
        # Enable signals again
        self.ui.tableWidget2DEditorXY.blockSignals(False)
        self.ui.tableWidget2DEditorXZ.blockSignals(False)
        self.ui.tableWidget2DEditorYZ.blockSignals(False)

    def updateSelectedCells(self, value, index):
        """Update from parameter tree.

        Args:
            value (float): Value to be updated in the table.
            index (int): Index of selected type of data.

        """
        items, methods, _ = self.itemsMethodsTable2DEditor()
        for item in items:
            self.dataEditor.setDataItem(eval(methods["x"]),
                                        eval(methods["y"]),
                                        eval(methods["z"]),
                                        value,
                                        index)

        self.updateObserverData()

    def enableGradient2DEditor(self):
        """Enable the gradient editor for 2D editor."""
        if (self.ui.tableWidget2DEditorXY.selectedItems() and
            self.ui.tableWidget2DEditorXY.hasFocus()) or \
            (self.ui.tableWidget2DEditorXZ.selectedItems() and
             self.ui.tableWidget2DEditorXZ.hasFocus()) or \
            (self.ui.tableWidget2DEditorYZ.selectedItems() and
             self.ui.tableWidget2DEditorYZ.hasFocus()):

            self.ui.action2DEditorGradient.setEnabled(True)
        else:
            self.ui.action2DEditorGradient.setEnabled(False)

    def itemsMethodsTable2DEditor(self):
        """Return current selected item, methods to access their indexes and the table.

        Returns:
            list (QtGui.QTableWidgetItem()), dict (string of methods), QtGui.QTableWidget():
            The current selected items, the methods attached to the selected table and the selected table

        Todo:
            This could be even better if getting these values, return just a new matrix
            with proper indexes and values to set data.

        """
        table = None
        item_methods = {}
        items = []

        if self.ui.tableWidget2DEditorXY.selectedItems():
            table = self.ui.tableWidget2DEditorXY
            items = table.selectedItems()
            item_methods = {"z": "self.ui.horizontalSlider2DEditorZIndex.value()",
                            "y": "item.row()",
                            "x": "item.column()"}

        elif self.ui.tableWidget2DEditorXZ.selectedItems():
            table = self.ui.tableWidget2DEditorXZ
            items = table.selectedItems()
            item_methods = {"z": "item.row()",
                            "y": "self.ui.horizontalSlider2DEditorYIndex.value()",
                            "x": "item.column()"}

        elif self.ui.tableWidget2DEditorYZ.selectedItems():
            table = self.ui.tableWidget2DEditorYZ
            items = table.selectedItems()
            item_methods = {"z": "item.row()",
                            "y": "item.column()",
                            "x": "self.ui.horizontalSlider2DEditorXIndex.value()"}

        return items, item_methods, table

    def gradient2DEditor(self):
        """Run the gradient editor and set values to 2D editor tables.

        Todo:
            Remove eval after changing itemMethodsTable2dEditor.

        """
        dialog = QtGui.QDialog()
        dialog_ui = Ui_DialogGradient()
        dialog_ui.setupUi(dialog)

        # Setting dialog_ui values
        cur_index = self.dataEditor.currentValuesIndex
        max_value = self.dataEditor.maximumValues[cur_index]
        min_value = self.dataEditor.minimumValues[cur_index]

        dialog_ui.doubleSpinBoxStart.setMaximum(max_value)
        dialog_ui.doubleSpinBoxStart.setMinimum(min_value)

        dialog_ui.doubleSpinBoxEnd.setMaximum(max_value)
        dialog_ui.doubleSpinBoxEnd.setMinimum(min_value)

        if dialog.exec():

            items, item_methods, table = self.itemsMethodsTable2DEditor()
            table.blockSignals(True)
            self.clearSelection2DEditor(all_tables=True)

            # this must be item.row or item.column
            method_index = ""

            # If gradient is applied to rows
            if dialog_ui.radioButtonRow.isChecked():
                method_index = "item.row()"
            # If gradient in applied to columns
            elif dialog_ui.radioButtonColumn.isChecked():
                method_index = "item.column()"

            # Use of eval it is not so good, but it works nicelly
            max_position = max([eval(method_index) for item in items])
            min_position = min([eval(method_index) for item in items])

            gradient = np.linspace(dialog_ui.doubleSpinBoxStart.value(),
                                   dialog_ui.doubleSpinBoxEnd.value(),
                                   max_position - min_position + 1)

            for item in items:
                self.dataEditor.setDataItem(eval(item_methods["x"]),
                                            eval(item_methods["y"]),
                                            eval(item_methods["z"]),
                                            gradient[eval(method_index) - min_position])

            table.blockSignals(False)

            self.dataEditor.updateObserversData()

    def updateDataFromTable2DEditor(self, item_changed):
        """Update data from table in 2D editor."""
        value = float(item_changed.text())

        _logger.debug("Value: %s", value)

        items, item_methods, table = self.itemsMethodsTable2DEditor()

        for item in items:
            self.dataEditor.setDataItem(eval(item_methods["x"]),
                                        eval(item_methods["y"]),
                                        eval(item_methods["z"]),
                                        value)

        self.updateObserverData()

    def tabify2DEditor(self, value):
        """Tabify 2D editor depending on value.

        Args:
            value (bool): Informs if the tables in 2DEditor should be tabified or not.

        """
        _logger.debug("Tabify: %s", value)

        if value:
            self.removeDockWidget(self.ui.dockWidget2DEditorXY)
            self.removeDockWidget(self.ui.dockWidget2DEditorXZ)
            self.removeDockWidget(self.ui.dockWidget2DEditorYZ)

            self.ui.dockWidget2DEditorXY.setVisible(True)
            self.ui.dockWidget2DEditorXZ.setVisible(True)
            self.ui.dockWidget2DEditorYZ.setVisible(True)

            self.addDockWidget(QtCore.Qt.DockWidgetArea(2), self.ui.dockWidget2DEditorXY)
            self.addDockWidget(QtCore.Qt.DockWidgetArea(2), self.ui.dockWidget2DEditorXZ)
            self.addDockWidget(QtCore.Qt.DockWidgetArea(2), self.ui.dockWidget2DEditorYZ)
        else:
            self.tabifyDockWidget(self.ui.dockWidget2DEditorXY, self.ui.dockWidget2DEditorXZ)
            self.tabifyDockWidget(self.ui.dockWidget2DEditorXZ, self.ui.dockWidget2DEditorYZ)

            if self.ui.action2DEditorYZ.isChecked():
                self.ui.dockWidget2DEditorYZ.raise_()

            elif self.ui.action2DEditorXZ.isChecked():
                self.ui.dockWidget2DEditorXZ.raise_()

            else:
                self.ui.dockWidget2DEditorXY.raise_()

    def invertBackground2DEditor(self, invert=False):
        """Invert the background color of 2D editor."""

    # 3D View ------------------------------------------------------------------

    def create3DView(self):
        """Create a 3D view and the first 3D object.

        It must be called when starts and when the shape or size is changed.
        """
        lx, ly, lz = self.dataEditor.size
        dx, dy, dz = self.dataEditor.elementSize
        nx, ny, nz = self.dataEditor.shape

        _logger.debug("Shape: %s, Size: %s",
                      (nx, ny, nz), (lx, ly, lz))

        # Camera configuration
        self.view3D = gl.GLViewWidget()

        camera_dist = 3 * max(lx, ly, lz)
        self.view3D.setCameraPosition(distance=camera_dist)

        self.dockWidgetMain.setWidget(self.view3D)

        # Grid configuration
        self.view3DGridX = gl.GLGridItem(antialias=True, glOptions="translucent")
        self.view3D.addItem(self.view3DGridX)

        self.view3DGridY = gl.GLGridItem(antialias=True, glOptions="translucent")
        self.view3D.addItem(self.view3DGridY)

        self.view3DGridZ = gl.GLGridItem(antialias=True, glOptions="translucent")
        self.view3D.addItem(self.view3DGridZ)

        self.view3DGridX.setVisible(self.ui.action3DViewXGrid.isChecked())
        self.view3DGridY.setVisible(self.ui.action3DViewYGrid.isChecked())
        self.view3DGridZ.setVisible(self.ui.action3DViewZGrid.isChecked())

        self.ui.action3DViewXGrid.triggered.connect(self.view3DGridX.setVisible)
        self.ui.action3DViewYGrid.triggered.connect(self.view3DGridY.setVisible)
        self.ui.action3DViewZGrid.triggered.connect(self.view3DGridZ.setVisible)

        self.translateGrid3DView()

        # Axis configuration
        self.view3DAxisX = gl.GLLinePlotItem(pos=np.array([[0, 0, 0], [(lx + 4) / 2, 0, 0]]),
                                             color=(255, 0, 0, 1), width=3.)
        self.view3DAxisX.setGLOptions(opts="opaque")
        self.view3DAxisX.setVisible(self.ui.action3DViewXYZAxis.isChecked())
        self.view3D.addItem(self.view3DAxisX)

        self.view3DAxisY = gl.GLLinePlotItem(pos=np.array([[0, 0, 0], [0, (ly + 4) / 2, 0]]),
                                             color=(0, 255, 0, 1), width=3.)
        self.view3DAxisY.setGLOptions(opts="opaque")
        self.view3DAxisY.setVisible(self.ui.action3DViewXYZAxis.isChecked())
        self.view3D.addItem(self.view3DAxisY)

        self.view3DAxisZ = gl.GLLinePlotItem(pos=np.array([[0, 0, 0], [0, 0, (lz + 4) / 2]]),
                                             color=(0, 0, 255, 1), width=3.)
        self.view3DAxisZ.setGLOptions(opts="opaque")
        self.view3DAxisZ.setVisible(self.ui.action3DViewXYZAxis.isChecked())
        self.view3D.addItem(self.view3DAxisZ)

        # Create 3D object
        def initialize_3d_item(x, y, z):
            """Create a new 3D item and put it in the view 3D.

            x (int): X index of the item.
            y (int): Y index of the item.
            z (int): Z index of the item.

            gl.GLMeshItem(): GL mesh item.

            """
            item = _get_element_3d_view([x, y, z], [dx, dy, dz], [lx, ly, lz])
            self.view3D.addItem(item)
            return item

        self.view3DObject = [[[initialize_3d_item(x, y, z)
                               for z in range(nz)]
                              for y in range(ny)]
                             for x in range(nx)]

        self.updateViewFromData3DView()

        # Background color setting
        if self.ui.action3DViewInvertBackground.isChecked():
            self.view3D.setBackgroundColor((255, 255, 255))

    def updateViewFromData3DView(self):
        """Color 3D view based on 3D data."""
        min_value = self.dataEditor.minimumValues[self.dataEditor.currentValuesIndex]
        max_value = self.dataEditor.maximumValues[self.dataEditor.currentValuesIndex]
        max_density = 1.

        if self.dataEditor.currentOpacityIndex != -1:
            max_density = self.dataEditor.maximumValues[self.dataEditor.currentOpacityIndex]

        rgb = self.colors[self.dataEditor.currentValuesIndex]

        _logger.debug("Value index: %s", self.dataEditor.currentValuesIndex)

        def color_settings(rgb, value, opacity):
            """Return color to color 3D view item.

            rgb (list(float)): List of minimum values of each color in rgb ([r, g, b] from 0. to 1.).
            value (float): value of data (from 0. to 1.).
            opacity (float): value of opacity(from 0. to 1.).

            tuple(float): Color in (r, g, b, a)

            """
            color = (rgb[0] + 0.6 * value,
                     rgb[1] + 0.6 * value,
                     rgb[2] + 0.6 * value,
                     0.5 * opacity)

            if not self.ui.action3DViewColor.isChecked():
                color = (1. + 0.6 * value,
                         1. + 0.6 * value,
                         1. + 0.6 * value,
                         0.5 * opacity)

            return color

        # Runs over the view3DObject changing color
        for index, item in np.ndenumerate(self.view3DObject):
            x, y, z = index
            value = (self.dataEditor.getDataItem(x, y, z) - max_value) / (min_value - max_value)
            opacity = 1.

            if self.dataEditor.currentOpacityIndex != -1:
                opacity = self.dataEditor.getDataItem(x, y, z, self.dataEditor.currentOpacityIndex) / max_density

            item.setColor(color_settings(rgb, value, opacity))

    def translateGrid3DView(self):
        """Translate grids to correct position."""
        lx, ly, lz = self.dataEditor.size
        dx, dy, dz = self.dataEditor.elementSize

        self.view3DGridX.resetTransform()
        self.view3DGridY.resetTransform()
        self.view3DGridZ.resetTransform()

        self.view3DGridX.setSize(z=lx + dx, y=ly + dy, x=lz + dz)
        self.view3DGridX.translate(dx=0, dy=0, dz=self.ui.spinBox2DEditorXIndex.value() * dx - lx / 2 + dx / 2)
        self.view3DGridX.rotate(90., 0, 1, 0)

        self.view3DGridY.setSize(x=lx + dx, y=lz + dz, z=ly + dy)
        self.view3DGridY.translate(dx=0, dy=0, dz=self.ui.spinBox2DEditorYIndex.value() * dy - ly / 2 + dy / 2)
        self.view3DGridY.rotate(-90., 1, 0, 0)

        self.view3DGridZ.setSize(x=lx + dx, y=ly + dy, z=lz + dz)
        self.view3DGridZ.translate(dx=0, dy=0, dz=self.ui.spinBox2DEditorZIndex.value() * dz - lz / 2 + dz / 2)

    def showAxis3DView(self, show=True):
        """Show axis in 3D view.

        Args:
            show (bool): Informs if the axis should be visible.

        """
        self.view3DAxisX.setVisible(show)
        self.view3DAxisY.setVisible(show)
        self.view3DAxisZ.setVisible(show)

    def invertBackground3DView(self, invert=False):
        """Invert the background color of 3D view.

        Args:
            invert (bool): Informs if the background color should be inverted.

        """
        if invert:
            self.view3D.setBackgroundColor((255, 255, 255))
        else:
            self.view3D.setBackgroundColor((0, 0, 0))

    # Graph View ---------------------------------------------------------------

    def plotSequence(self):
        """Use the data from a sequence to create the RF and Gradient plots."""
        self.graphicsSequence = pg.GraphicsWindow()
        self.dockWidgetMain.setWidget(self.graphicsSequence)

        rf = self.sequenceExample.rf
        gradient = self.sequenceExample.gr
        time = self.sequenceExample.tp

        rf_am = np.absolute(rf)
        rf_pm = np.angle(rf, deg=False)
        rf_fm = np.gradient(rf_pm, time[0] - time[1])

        gradient_x = gradient[0]
        gradient_y = gradient[1]
        gradient_z = gradient[2]

        rf_am_plot = plot_item(self.graphicsSequence, time, rf_am, "y", False, "", "", True, "RF (AM)", "G")
        rf_pm_plot = plot_item(self.graphicsSequence, time, rf_pm, "c", False, "", "", True, "RF (PM)", "rad")
        rf_pm_plot.getAxis('left').setTicks([[(np.pi, chr(960)), (np.pi / 2, chr(960) + '/2'), (0.0, '0'), (-np.pi, '-' + chr(960)), (-np.pi / 2, '-' + chr(960) + '/2')]])
        rf_fm_plot = plot_item(self.graphicsSequence, time, rf_fm, "m", False, "", "", True, "RF (FM)", "Hz")

        gr_x_plot = plot_item(self.graphicsSequence, time, gradient_x, "r", False, "", "", True, "Gr (x)", "G/cm")
        gr_y_plot = plot_item(self.graphicsSequence, time, gradient_y, "g", False, "", "", True, "Gr (y)", "G/cm")
        gr_z_plot = plot_item(self.graphicsSequence, time, gradient_z, "b", True, "Time", "s", True, "Gr (z)", "G/cm")

        plot = [rf_am_plot, rf_pm_plot, rf_fm_plot, gr_x_plot, gr_y_plot, gr_z_plot]
        for i in range(len(plot) - 1):
            plot[i].getViewBox().setXLink(plot[i + 1].getViewBox())

        timelines = [pg.InfiniteLine(pos=0, angle=90, pen="w", movable=True, bounds=(time[0], time[len(time) - 1] * 0.999)) for i in plot]

        def updateTimelines():
            """Function to set the same value for all timelines."""

            indexes = [1 for i in range(len(timelines))]
            for i in range(len(timelines)):
                if(timelines[i].value() == timelines[np.mod(i + 1, len(timelines))].value()):
                    indexes[i] = 0
                    indexes[np.mod(i + 1, len(timelines))] = 0
            if(1 in indexes):
                value = timelines[indexes.index(1)].value()
                for timeline in timelines:
                    timeline.blockSignals(True)
                    timeline.setValue(value)
                    timeline.blockSignals(False)

        for i in range(len(plot)):
            plot[i].addItem(timelines[i])
            timelines[i].sigPositionChanged.connect(updateTimelines)

    # Simulation ---------------------------------------------------------------

    def simulate(self):
        """Setup a simulation."""
        # opening file
        sample_file = h5py.File(self.filepath["Sample"], 'r')
        sample_group = sample_file.require_group("SampleGroup")

        # reading sample file
        sample_param_dset = sample_group.require_dataset("param", exact=True, shape=(9,), dtype=float)
        sample_shape = tuple(sample_group.require_dataset("shape", exact=True, shape=(4,), dtype=int).value)
        sample_data_dset = sample_group.require_dataset("data", exact=True, shape=sample_shape, dtype=float)

        # creating positions
        sample_size = [sample_param_dset.value[i] for i in [0, 1, 2]]
        sample_dimension = [int(sample_param_dset.value[3 + i]) for i in [0, 1, 2]]
        sample_step = [sample_size[i] / sample_dimension[i] for i in [0, 1, 2]]
        sample_offset = [-sample_size[i] / 2 + sample_step[i] / 2 for i in [0, 1, 2]]
        sample_position = create_positions(size=sample_size, step=sample_step, offset=sample_offset)

        freq_shift = frequency_shift(5, 1, 0)
        mode = 2

        number_voxels = sample_dimension[0] * sample_dimension[1] * sample_dimension[2]
        magnetization_size = sample_step[2] / 2

        rf = self.sequenceExample.rf
        gr = self.sequenceExample.gr
        dt = self.sequenceExample.dt
        tp = self.sequenceExample.tp
        t1 = np.zeros(number_voxels)
        t2 = np.zeros(number_voxels)
        rho = np.zeros(number_voxels)

        index = 0
        for k in range(sample_dimension[2]):
            for j in range(sample_dimension[1]):
                for i in range(sample_dimension[0]):
                    t1[index] = sample_data_dset[i, j, k, 0]
                    t2[index] = sample_data_dset[i, j, k, 1]
                    rho[index] = sample_data_dset[i, j, k, 2]
                    index += 1

        mx, my, mz = evolve(rf, gr, dt, t1, t2, freq_shift, sample_position, mode)

        # Apply density of nuclei effect

        mx = np.transpose(mx, (1, 0, 2))
        my = np.transpose(my, (1, 0, 2))
        mz = np.transpose(mz, (1, 0, 2))

        for i in range(number_voxels):
            mx[i] *= rho[i] * magnetization_size
            my[i] *= rho[i] * magnetization_size
            mz[i] *= rho[i] * magnetization_size

        mx = np.transpose(mx, (1, 0, 2))
        my = np.transpose(my, (1, 0, 2))
        mz = np.transpose(mz, (1, 0, 2))

        self.plot = Plot(self.settings, mx, my, mz, gr, tp, freq_shift, sample_position, magnetization_size)
        self.plot.plotMagnetization(self.graphicsMagnetization)
        self.plot.plotSpin(self.spinView3D)

        if self.settings.simulator_group.showSample.value():
            nx, ny, nz = sample_dimension
            for x in range(nx):
                for y in range(ny):
                    for z in range(nz):
                        item = _get_element_3d_view([x, y, z], sample_step, sample_size)
                        item.setColor((1, 1, 1, 0.06))
                        self.spinView3D.addItem(item)

        if self.settings.simulator_group.showMagnet.value():
            x = self.settings.magnet_config_group.SizeX.value()
            y = self.settings.magnet_config_group.SizeY.value()
            z = self.settings.magnet_config_group.SizeZ.value()
            magnet = _get_element_3d_view([0, 0, 0], [x, y, z], [x, y, z])
            magnet.setColor((1, 1, 1, 0.03))
            self.spinView3D.addItem(magnet)

        self.ui.actionSimulatorRun.setEnabled(True)
        self.ui.actionSimulatorPlay.setEnabled(False)
        self.ui.actionSimulatorPause.setEnabled(False)
        self.ui.actionSimulatorStop.setEnabled(False)
        self.ui.actionSimulatorCalculate.setEnabled(False)

        self.ui.actionSimulatorRun.triggered.connect(self.simulationRun)
        self.ui.actionSimulatorPlay.triggered.connect(self.simulationPlay)
        self.ui.actionSimulatorPause.triggered.connect(self.simulationPause)
        self.ui.actionSimulatorStop.triggered.connect(self.simulationStop)

    def simulationRun(self):
        """Start the simulation from beginning."""
        self.ui.actionSimulatorRun.setEnabled(False)
        self.ui.actionSimulatorPlay.setEnabled(False)
        self.ui.actionSimulatorPause.setEnabled(True)
        self.ui.actionSimulatorStop.setEnabled(True)
        self.plot.run()

    def simulationPlay(self):
        """Restart the simulation from where it is."""
        self.ui.actionSimulatorRun.setEnabled(False)
        self.ui.actionSimulatorPlay.setEnabled(False)
        self.ui.actionSimulatorPause.setEnabled(True)
        self.ui.actionSimulatorStop.setEnabled(True)
        self.plot.play()

    def simulationPause(self):
        """Pause the simulation."""
        self.ui.actionSimulatorRun.setEnabled(False)
        self.ui.actionSimulatorPlay.setEnabled(True)
        self.ui.actionSimulatorPause.setEnabled(False)
        self.ui.actionSimulatorStop.setEnabled(True)
        self.plot.pause()

    def simulationStop(self):
        """Stop the simulation."""
        self.ui.actionSimulatorRun.setEnabled(True)
        self.ui.actionSimulatorPlay.setEnabled(False)
        self.ui.actionSimulatorPause.setEnabled(False)
        self.ui.actionSimulatorStop.setEnabled(False)
        self.plot.pause()

    # File ---------------------------------------------------------------------

    def open(self, file_path):
        """Open a HDF5 file and applies the changes to the program.

        Args:
            file_path (str): Path to the file where the data will be opened.

        """
        _logger.info("File path to open: %s", file_path)

        context = ""

        if self.ui.actionContextSample.isChecked():
            self.openSample(file_path)
            context = "Sample"
        elif self.ui.actionContextSystem.isChecked():
            self.openSystem(file_path)
            context = "System"
        elif self.ui.actionContextSequence.isChecked():
            self.openSequence(file_path)
            context = "Sequence"

        self.filepath[context] = file_path

    def save(self, file_path):
        """Create a HDF5 file to save current data.

        Args:
            file_path (str): Path to the file where the data will be saved.

        """
        _logger.debug("File path to save: %s", file_path)

        context = ""
        if self.ui.actionContextSample.isChecked():
            self.saveSample(file_path)
            context = "Sample"
        elif self.ui.actionContextSystem.isChecked():
            self.saveSystem(file_path)
            context = "System"
        self.filepath[context] = file_path

    def canClose(self):
        """Check if the user want to save the sample before closing.

        Returns:
            bool: True if can close.

        """
        if self.fileChanged:
            close_dialog = QtGui.QMessageBox()
            close_dialog.setWindowTitle("Close")
            close_dialog.setText("Do you want to save your changes?")
            close_dialog.setStandardButtons(QtGui.QMessageBox.Save |
                                            QtGui.QMessageBox.Discard |
                                            QtGui.QMessageBox.Cancel)
            close_dialog.setDefaultButton(QtGui.QMessageBox.Save)
            answer = close_dialog.exec()

            if answer == QtGui.QMessageBox.Save:
                self.fileSave()
                return 1
            elif answer == QtGui.QMessageBox.Cancel:
                return 0
            elif answer == QtGui.QMessageBox.Discard:
                _logger.debug("Discarding changes: %s", self.filepath)
                return 1
            else:
                return 0
        else:
            return 1

    def fileOpen(self):
        """Open a dialog to select a HDF5 file to be opened."""
        if self.canClose():
            file_dialog = QtGui.QFileDialog(caption="Open ...")
            file_dialog.setNameFilter("*" + self.currentExtension)
            file_dialog.setAcceptMode(QtGui.QFileDialog.AcceptOpen)

            if file_dialog.exec():
                file_path = file_dialog.selectedFiles()[0]
                if file_path:
                    self.open(file_path)

    def fileNew(self):
        """Restart the edition from start."""
        if self.canClose():
            context = ""
            if self.ui.actionContextSample.isChecked():
                self.loadSampleParameters()
                context = "Sample"
            elif self.ui.actionContextSystem.isChecked():
                self.loadSystemParameters()
                context = "System"
            self.filepath[context] = ""
            self.fileChanged = False

    def fileSave(self):
        """Save the current sample in the last saving file.

        If there is no current saving file, it calls fileSaveAs().

        """
        context = ""
        if self.ui.actionContextSample.isChecked():
            context = "Sample"
        elif self.ui.actionContextSystem.isChecked():
            context = "System"

        if not self.filepath[context]:
            self.fileSaveAs()
        else:
            self.save(self.filepath[context])

    def fileSaveAs(self):
        """Open a dialog to select the current saving file."""
        file_dialog = QtGui.QFileDialog(caption="Save as ...")
        file_dialog.setNameFilter("*" + self.currentExtension)
        file_dialog.setAcceptMode(QtGui.QFileDialog.AcceptSave)

        if file_dialog.exec():
            file_path = file_dialog.selectedFiles()[0]
            if file_path[-len(self.currentExtension):] != self.currentExtension:
                file_path += self.currentExtension
            if file_path:
                self.save(file_path)

    def fileClose(self):
        """Close file and create a new one."""
        _logger.debug("Closing: %s", self.filepath)
        self.fileNew()

    def quit(self):
        """Close the main window."""
        _logger.debug("Quit application")
        if self.canClose():
            self.close()

    # File (Sample) ---------------------------------------------------------------------

    def openSample(self, file_path):
        """Open a HDF5 sample file.

        Args:
            file_path (str): Path to a file containing a sample.

        """
        file_ = h5py.File(file_path, "r")
        sample_group = file_.require_group("SampleGroup")

        # Reading datasets
        param_dset = sample_group.require_dataset("param", exact=True, shape=(9,), dtype=float)
        shape_ = tuple(sample_group.require_dataset("shape", exact=True, shape=(4,), dtype=int).value)
        data_dset = sample_group.require_dataset("data", exact=True, shape=shape_, dtype=float)

        # Updating changes
        size = param_dset.value[0:3]
        shape = [int(n) for n in param_dset.value[3:6]]
        self.dataEditor.setDimension(size, shape)

        lx, ly, lz = self.dataEditor.size
        nx, ny, nz = self.dataEditor.shape

        self.sample.Nx.setValue(nx)
        self.sample.Ny.setValue(ny)
        self.sample.Nz.setValue(nz)

        self.sample.SizeX.setValue(lx)
        self.sample.SizeY.setValue(ly)
        self.sample.SizeZ.setValue(lz)

        self.dataEditor.data = data_dset.value
        file_.close()

    def saveSample(self, file_path):
        """Save a HDF5 sample file.

        Args:
            file_path (str): Path to the file where the sample will be saved.

        """
        file_ = h5py.File(file_path, "w")
        sample_group = file_.create_group("SampleGroup")
        param_list = [param.value() for param in self.sample]

        # Creating datasets
        param_dset = sample_group.create_dataset("param", data=param_list)
        shape_dset = sample_group.create_dataset("shape", data=self.dataEditor.data.shape[0:4])
        data_dset = sample_group.create_dataset("data", data=self.dataEditor.data[:, :, :, :])

        file_.flush()
        file_.close()

    # File (System) ---------------------------------------------------------------------

    def openSystem(self, file_path):
        """Open a HDF5 system file.

        Args:
            file_path (str): Path to a file containing the system.

        """
        file_ = h5py.File(file_path, "r")
        system_group = file_.require_group("SystemGroup")

        # Reading datasets
        n = system_group.require_dataset("shape", exact=True, shape=(), dtype=int).value
        shape_ = (n, n, n, 3)
        nucleus = system_group.require_dataset("nucleus", exact=True, shape=(), dtype=object).value
        magnetic_strength = system_group.require_dataset("magnet", shape=(), dtype=float).value
        data_dset = system_group.require_dataset("data", exact=True, shape=shape_, dtype=float)

        # Updating changes
        self.magnet.magneticStrength.setValue(magnetic_strength)
        self.nucleus.nucleus.setValue(nucleus)
        self.dataEditor.setDimension(self.magnetSize, [n, n, n])
        self.resolution.N.setValue(n)

        self.dataEditor.data = data_dset.value
        file_.close()

    def saveSystem(self, file_path):
        """Save a HDF5 system file.

        Args:
            file_path (str): Path to the file where the system will be saved.

        """
        file_ = h5py.File(file_path, "w")
        system_group = file_.create_group("SystemGroup")

        # Creating datasets
        shape_dset = system_group.create_dataset("shape", data=self.resolution.N.value())
        nucleus_dset = system_group.create_dataset("nucleus", data=self.nucleus.nucleus.value())
        magnet_dset = system_group.create_dataset("magnet", data=self.magnet.magneticStrength.value(), dtype=float)
        data_dset = system_group.create_dataset("data", data=self.dataEditor.data[:, :, :, :])

        file_.flush()
        file_.close()

    # File (Sequence) ---------------------------------------------------------------------

    def openSequence(self, file_path):
        """Open a python sequence file.

        The file must contain a class SequenceExample, that contains
        information about the sequence as RF pulses and the Gradient.

        Args:
            file_path (str): Path to a file containing the sequence.


        """
        imp.load_source("sequence", file_path)
        import sequence

        self.sequenceExample = sequence.SequenceExample(self.settings, self.nucleus)

        for param in self.sequenceExample:
            param.sigValueChanged.connect(self.plotSequence)

        self.parameterTree.clear()
        self.parameterTree.addParameters(self.sequenceExample)

        self.plotSequence()

    def closeEvent(self, event):
        """Method called when the window is closing."""
        _logger.debug("file.ini updated")
        fileIni = open(self.pathIni, "w")
        fileIni.write("CONFIG_PATH=" + str(self.filepath["Config"]) + "\n")
        fileIni.write("SAMPLE_PATH=" + str(self.filepath["Sample"]) + "\n")
        fileIni.write("SYSTEM_PATH=" + str(self.filepath["System"]) + "\n")
        fileIni.write("SEQUENCE_PATH=" + str(self.filepath["Sequence"]) + "\n")
        fileIni.flush()
        fileIni.close()
