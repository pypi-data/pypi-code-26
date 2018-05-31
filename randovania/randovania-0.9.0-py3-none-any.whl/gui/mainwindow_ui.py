# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:\programming\projects\randovania\randovania/gui\mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 400)
        MainWindow.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.centralWidget = QtWidgets.QWidget(MainWindow)
        self.centralWidget.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.centralWidget.setObjectName("centralWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralWidget)
        self.gridLayout.setContentsMargins(11, 11, 11, 11)
        self.gridLayout.setSpacing(6)
        self.gridLayout.setObjectName("gridLayout")
        self.tabWidget = QtWidgets.QTabWidget(self.centralWidget)
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.tab)
        self.gridLayout_2.setContentsMargins(11, 11, 11, 11)
        self.gridLayout_2.setSpacing(6)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label = QtWidgets.QLabel(self.tab)
        self.label.setObjectName("label")
        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tab, "")
        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralWidget)
        self.menuBar = QtWidgets.QMenuBar(MainWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 800, 21))
        self.menuBar.setObjectName("menuBar")
        MainWindow.setMenuBar(self.menuBar)

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Randovania"))
        self.label.setText(_translate("MainWindow", "<html><head/><body><p><span style=\" font-size:12pt;\">Randovania</span></p><p><a href=\"https://github.com/henriquegemignani/randovania\"><span style=\" font-size:10pt; text-decoration: underline; color:#0000ff;\">https://github.com/henriquegemignani/randovania</span></a></p><p><br/></p><p><span style=\" font-size:10pt;\">This software is covered by the </span><a href=\"https://www.gnu.org/licenses/gpl-3.0.en.html\"><span style=\" font-size:10pt; text-decoration: underline; color:#0000ff;\">GNU General Public License v3 (GPL v3)</span></a><span style=\" font-size:10pt;\">.</span></p><p><br/></p><p><span style=\" font-size:10pt;\">Written by </span><a href=\"https://github.com/henriquegemignani/\"><span style=\" font-size:10pt; text-decoration: underline; color:#0000ff;\">Henrique Gemignani</span></a></p><p><span style=\" font-size:10pt;\">Metroid Prime 2 room data collected by </span><a href=\"https://twitter.com/ClarisRobyn\"><span style=\" font-size:10pt; text-decoration: underline; color:#0000ff;\">Claris</span></a></p><p><span style=\" font-size:10pt;\">Randomizer also written by Claris</span></p></body></html>"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("MainWindow", "About"))

