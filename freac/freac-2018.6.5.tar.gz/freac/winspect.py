#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import numpy as np
from PyQt5 import QtCore, QtWidgets
import pyqtgraph as pg
from pyqtgraph import dockarea
import cryio
from freac.ui.qinspect import Ui_WInspect


class WInspect(QtWidgets.QMainWindow, Ui_WInspect):
    def __init__(self, parent=None):
        super(WInspect, self).__init__(parent)
        self.frames = []
        self.setupUi()
        self.initMovieTimer()
        self.initROI(True)

    def initMovieTimer(self):
        self.movieTimer = QtCore.QTimer(self)
        # noinspection PyUnresolvedReferences
        self.movieTimer.timeout.connect(self.slideMovie)

    def initROI(self, new=False):
        xc, yc = self.getImageCenter()
        if new:
            self.roi = pg.PolyLineROI([[xc, yc], [xc - 100, yc - 100], [xc - 100, yc + 100]],
                                      closed=True, removable=True)
            self.roi.sigRegionChanged.connect(self.roiRegionChanged)
            self.image.getView().addItem(self.roi)
            self.roi.setVisible(False)

    def slideMovie(self):
        current = self.slider.value()
        if current == self.slider.maximum():
            self.movieTimer.stop()
            self.actionRun.setChecked(False)
        else:
            self.slider.setSliderPosition(current + 1)

    def setupUi(self, *args, **kwargs):
        Ui_WInspect.setupUi(self, self)
        self.setDockArea()
        self.image.ui.roiBtn.hide()
        self.image.ui.menuBtn.hide()
        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider.setDisabled(True)
        self.slider.setMinimum(0)
        # noinspection PyUnresolvedReferences
        self.slider.valueChanged.connect(self.sliderMoved)
        self.toolBar.addWidget(self.slider)
        self.wprogress = QtWidgets.QProgressDialog(self)
        self.loadSettings()

    def setDockArea(self):
        self.dock = dockarea.DockArea()
        self.setCentralWidget(self.dock)
        d1 = dockarea.Dock('Image')
        d2 = dockarea.Dock('Integration')
        self.dock.addDock(d1, 'left')
        self.dock.addDock(d2, 'right')
        self.image = pg.ImageView()
        self.plot = pg.PlotWidget()
        d1.addWidget(self.image)
        d2.addWidget(self.plot)

    def saveSettings(self):
        s = QtCore.QSettings()
        s.setValue('WInspect/Geometry', self.saveGeometry())
        s.setValue('WInspect/State', self.saveState())
        s.setValue('WInspect/lastdir', self.lastdir)
        s.setValue('WInspect/dataDockState', json.dumps(self.dock.saveState()))

    def loadSettings(self):
        s = QtCore.QSettings()
        self.restoreGeometry(s.value('WInspect/Geometry', QtCore.QByteArray()))
        self.restoreState(s.value('WInspect/State', QtCore.QByteArray()))
        self.lastdir = s.value('WInspect/lastdir', '')
        dockState = s.value('WInspect/dataDockState', None)
        if dockState:
            self.dock.restoreState(json.loads(dockState))

    def closeEvent(self, event):
        self.saveSettings()

    @QtCore.pyqtSlot()
    def on_actionOpenDirectory_triggered(self):
        # noinspection PyCallByClass,PyTypeChecker
        dire = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select directory', self.lastdir)
        if not dire:
            return
        self.lastdir = dire
        self.wprogress.show()
        nImages = self.loadImages(dire)
        if not nImages:
            return
        self.slider.setEnabled(True)
        self.slider.setMaximum(nImages - 1)
        self.image.setImage(self.frames[0].array)

    def loadImages(self, dire):
        files = os.listdir(dire)
        files.sort()
        self.frames = []
        for i, fimg in enumerate(files):
            self.wprogress.setValue(int(i / len(files) * 100))
            if self.wprogress.wasCanceled():
                self.frames = []
                break
            try:
                img = cryio.openImage(os.path.join(dire, fimg))
            except cryio.ImageError:
                continue
            if os.path.splitext(fimg)[1] == '.cbf':
                img.array = np.rot90(img.array[::-1], 3)
            self.frames.append(img)
        self.wprogress.setValue(100)
        return len(self.frames)

    def sliderMoved(self, value):
        frame = self.frames[value]
        self.image.setImage(frame.array, autoRange=False, autoLevels=False)
        self.statusbar.showMessage(frame.filepath)

    @QtCore.pyqtSlot(bool)
    def on_actionRun_triggered(self, checked):
        if self.slider.value() == self.slider.maximum():
            self.slider.setValue(0)
        if checked:
            self.movieTimer.setInterval(1000)
            self.movieTimer.start()
        else:
            self.movieTimer.stop()

    @QtCore.pyqtSlot(bool)
    def on_actionROI_triggered(self, checked):
        self.roi.setVisible(checked)

    def roiRegionChanged(self, roi=None):
        roisum = self.roi.getArrayRegion(self.frames[self.slider.value()].array, self.image.getImageItem()).sum()

    def getImageCenter(self):
        ranges = self.image.getView().getState()['viewRange']
        return ranges[0][1] // 2, ranges[1][1] // 2
