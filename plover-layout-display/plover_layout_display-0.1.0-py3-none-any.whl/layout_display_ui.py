# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'layout_display/layout_display.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_LayoutDisplay(object):
    def setupUi(self, LayoutDisplay):
        LayoutDisplay.setObjectName("LayoutDisplay")
        LayoutDisplay.resize(350, 200)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(LayoutDisplay.sizePolicy().hasHeightForWidth())
        LayoutDisplay.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("Monospace")
        LayoutDisplay.setFont(font)
        LayoutDisplay.setSizeGripEnabled(True)
        self.verticalLayout = QtWidgets.QVBoxLayout(LayoutDisplay)
        self.verticalLayout.setObjectName("verticalLayout")
        self.grid_layout = QtWidgets.QGridLayout()
        self.grid_layout.setObjectName("grid_layout")
        self.button_load = QtWidgets.QPushButton(LayoutDisplay)
        self.button_load.setObjectName("button_load")
        self.grid_layout.addWidget(self.button_load, 1, 2, 1, 1)
        self.label_layout_name = QtWidgets.QLabel(LayoutDisplay)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_layout_name.sizePolicy().hasHeightForWidth())
        self.label_layout_name.setSizePolicy(sizePolicy)
        self.label_layout_name.setObjectName("label_layout_name")
        self.grid_layout.addWidget(self.label_layout_name, 1, 0, 1, 1)
        self.button_reset = QtWidgets.QPushButton(LayoutDisplay)
        self.button_reset.setObjectName("button_reset")
        self.grid_layout.addWidget(self.button_reset, 1, 1, 1, 1)
        self.verticalLayout.addLayout(self.grid_layout)
        self.layout_display_view = LayoutDisplayView(LayoutDisplay)
        self.layout_display_view.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.layout_display_view.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.layout_display_view.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.layout_display_view.setRenderHints(QtGui.QPainter.Antialiasing|QtGui.QPainter.TextAntialiasing)
        self.layout_display_view.setObjectName("layout_display_view")
        self.verticalLayout.addWidget(self.layout_display_view)

        self.retranslateUi(LayoutDisplay)
        QtCore.QMetaObject.connectSlotsByName(LayoutDisplay)

    def retranslateUi(self, LayoutDisplay):
        _translate = QtCore.QCoreApplication.translate
        LayoutDisplay.setWindowTitle(_translate("LayoutDisplay", "Layout Display"))
        self.button_load.setToolTip(_translate("LayoutDisplay", "Select a layout file to load"))
        self.button_load.setText(_translate("LayoutDisplay", "Load"))
        self.label_layout_name.setAccessibleName(_translate("LayoutDisplay", "Layout Name"))
        self.label_layout_name.setAccessibleDescription(_translate("LayoutDisplay", "The currently loaded layout\'s name"))
        self.label_layout_name.setText(_translate("LayoutDisplay", "Default Layout Name"))
        self.button_reset.setToolTip(_translate("LayoutDisplay", "Reset the layout to the default"))
        self.button_reset.setText(_translate("LayoutDisplay", "Reset"))
        self.layout_display_view.setAccessibleName(_translate("LayoutDisplay", "Layout Display Area"))
        self.layout_display_view.setAccessibleDescription(_translate("LayoutDisplay", "The display area for the loaded layout"))

from layout_display.layout_graphics import LayoutDisplayView
from . import resources_rc
