# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'androidpermissionsdialog.ui'
#
# Created by: PyQt5 UI code generator 5.10
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_AndroidPermissionsDialog(object):
    def setupUi(self, AndroidPermissionsDialog):
        AndroidPermissionsDialog.setObjectName("AndroidPermissionsDialog")
        AndroidPermissionsDialog.resize(640, 566)
        self.gridLayout = QtWidgets.QGridLayout(AndroidPermissionsDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.scrollArea = QtWidgets.QScrollArea(AndroidPermissionsDialog)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 616, 455))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridPermissions = QtWidgets.QGridLayout()
        self.gridPermissions.setObjectName("gridPermissions")
        self.verticalLayout.addLayout(self.gridPermissions)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.gridLayout.addWidget(self.scrollArea, 2, 1, 1, 1)
        self.label_6 = QtWidgets.QLabel(AndroidPermissionsDialog)
        self.label_6.setObjectName("label_6")
        self.gridLayout.addWidget(self.label_6, 1, 1, 1, 1)
        self.buttonBox = QtWidgets.QDialogButtonBox(AndroidPermissionsDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 4, 1, 1, 1)
        self.permissionsList = QtWidgets.QLineEdit(AndroidPermissionsDialog)
        self.permissionsList.setReadOnly(True)
        self.permissionsList.setObjectName("permissionsList")
        self.gridLayout.addWidget(self.permissionsList, 3, 1, 1, 1)

        self.retranslateUi(AndroidPermissionsDialog)
        self.buttonBox.accepted.connect(AndroidPermissionsDialog.accept)
        self.buttonBox.rejected.connect(AndroidPermissionsDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(AndroidPermissionsDialog)

    def retranslateUi(self, AndroidPermissionsDialog):
        _translate = QtCore.QCoreApplication.translate
        AndroidPermissionsDialog.setWindowTitle(_translate("AndroidPermissionsDialog", "About Buildertron..."))
        self.label_6.setText(_translate("AndroidPermissionsDialog", "Note: Ensure you understand the usage of permissions before adding to the spec."))

