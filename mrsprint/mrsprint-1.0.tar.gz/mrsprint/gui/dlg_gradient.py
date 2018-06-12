# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'sampleGradient.ui'
#
# Created: Fri Jun 16 07:53:50 2017
#      by: pyside-uic 0.2.15 running on PySide 1.2.4
#
# WARNING! All changes made in this file will be lost!

from pyqtgraph.Qt import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)


class Ui_DialogGradient(object):
    def setupUi(self, DialogGradient):
        dialogGradient.setObjectName("dialogGradient")
        dialogGradient.resize(312, 269)
        dialogGradient.setMinimumSize(QtCore.QSize(312, 269))
        dialogGradient.setMaximumSize(QtCore.QSize(312, 269))
        self.buttonBox = QtGui.QDialogButtonBox(dialogGradient)
        self.buttonBox.setGeometry(QtCore.QRect(20, 220, 271, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayoutWidget = QtGui.QWidget(dialogGradient)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(20, 20, 271, 181))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtGui.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.labelDescription1 = QtGui.QLabel(self.verticalLayoutWidget)
        self.labelDescription1.setObjectName("labelDescription1")
        self.verticalLayout.addWidget(self.labelDescription1)
        self.radioButtonRow = QtGui.QRadioButton(self.verticalLayoutWidget)
        self.radioButtonRow.setChecked(True)
        self.radioButtonRow.setObjectName("radioButtonRow")
        self.verticalLayout.addWidget(self.radioButtonRow)
        self.radioButtonColumn = QtGui.QRadioButton(self.verticalLayoutWidget)
        self.radioButtonColumn.setObjectName("radioButtonColumn")
        self.verticalLayout.addWidget(self.radioButtonColumn)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.labelDescription2 = QtGui.QLabel(self.verticalLayoutWidget)
        self.labelDescription2.setObjectName("labelDescription2")
        self.verticalLayout.addWidget(self.labelDescription2)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.labelDescription3 = QtGui.QLabel(self.verticalLayoutWidget)
        self.labelDescription3.setObjectName("labelDescription3")
        self.horizontalLayout.addWidget(self.labelDescription3)
        self.doubleSpinBoxStart = QtGui.QDoubleSpinBox(self.verticalLayoutWidget)
        self.doubleSpinBoxStart.setObjectName("doubleSpinBoxStart")
        self.horizontalLayout.addWidget(self.doubleSpinBoxStart)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.labelDescription4 = QtGui.QLabel(self.verticalLayoutWidget)
        self.labelDescription4.setObjectName("labelDescription4")
        self.horizontalLayout_2.addWidget(self.labelDescription4)
        self.doubleSpinBoxEnd = QtGui.QDoubleSpinBox(self.verticalLayoutWidget)
        self.doubleSpinBoxEnd.setObjectName("doubleSpinBoxEnd")
        self.horizontalLayout_2.addWidget(self.doubleSpinBoxEnd)
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem2)
        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.retranslateUi(dialogGradient)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), dialogGradient.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), dialogGradient.reject)
        QtCore.QMetaObject.connectSlotsByName(dialogGradient)
        dialogGradient.setTabOrder(self.radioButtonRow, self.radioButtonColumn)
        dialogGradient.setTabOrder(self.radioButtonColumn, self.doubleSpinBoxStart)
        dialogGradient.setTabOrder(self.doubleSpinBoxStart, self.doubleSpinBoxEnd)
        dialogGradient.setTabOrder(self.doubleSpinBoxEnd, self.buttonBox)

    def retranslateUi(self, dialogGradient):
        dialogGradient.setWindowTitle(QtGui.QApplication.translate("dialogGradient", "Setting a gradient", None, QtGui.QApplication.UnicodeUTF8))
        self.labelDescription1.setText(QtGui.QApplication.translate("dialogGradient", "Set the gradient to:", None, QtGui.QApplication.UnicodeUTF8))
        self.radioButtonRow.setText(QtGui.QApplication.translate("dialogGradient", "Rows", None, QtGui.QApplication.UnicodeUTF8))
        self.radioButtonColumn.setText(QtGui.QApplication.translate("dialogGradient", "Columns", None, QtGui.QApplication.UnicodeUTF8))
        self.labelDescription2.setText(QtGui.QApplication.translate("dialogGradient", "Adjust the gradient range", None, QtGui.QApplication.UnicodeUTF8))
        self.labelDescription3.setText(QtGui.QApplication.translate("dialogGradient", "Start", None, QtGui.QApplication.UnicodeUTF8))
        self.labelDescription4.setText(QtGui.QApplication.translate("dialogGradient", "End", None, QtGui.QApplication.UnicodeUTF8))

