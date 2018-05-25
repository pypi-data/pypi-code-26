# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'forms/main_window.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(350, 401)
        MainWindow.setUnifiedTitleAndToolBarOnMac(True)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.cameraPlot = QtWidgets.QWidget(self.centralwidget)
        self.cameraPlot.setMinimumSize(QtCore.QSize(100, 100))
        self.cameraPlot.setStyleSheet("border-color: black;\n"
"border-width: 2px;\n"
"border-style: solid;")
        self.cameraPlot.setObjectName("cameraPlot")
        self.verticalLayout.addWidget(self.cameraPlot)
        self.scatterPlot = QtWidgets.QWidget(self.centralwidget)
        self.scatterPlot.setMinimumSize(QtCore.QSize(100, 100))
        self.scatterPlot.setStyleSheet("border-color: black;\n"
"border-width: 2px;\n"
"border-style: solid;")
        self.scatterPlot.setObjectName("scatterPlot")
        self.verticalLayout.addWidget(self.scatterPlot)
        self.horizontalLayout_4.addLayout(self.verticalLayout)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.centroidXPlot = QtWidgets.QWidget(self.centralwidget)
        self.centroidXPlot.setMinimumSize(QtCore.QSize(100, 100))
        self.centroidXPlot.setStyleSheet("border-color: black;\n"
"border-width: 2px;\n"
"border-style: solid;")
        self.centroidXPlot.setObjectName("centroidXPlot")
        self.horizontalLayout.addWidget(self.centroidXPlot)
        self.centroidYPlot = QtWidgets.QWidget(self.centralwidget)
        self.centroidYPlot.setMinimumSize(QtCore.QSize(100, 100))
        self.centroidYPlot.setStyleSheet("border-color: black;\n"
"border-width: 2px;\n"
"border-style: solid;")
        self.centroidYPlot.setObjectName("centroidYPlot")
        self.horizontalLayout.addWidget(self.centroidYPlot)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.fftXPlot = QtWidgets.QWidget(self.centralwidget)
        self.fftXPlot.setMinimumSize(QtCore.QSize(100, 100))
        self.fftXPlot.setStyleSheet("border-color: black;\n"
"border-width: 2px;\n"
"border-style: solid;")
        self.fftXPlot.setObjectName("fftXPlot")
        self.horizontalLayout_2.addWidget(self.fftXPlot)
        self.fftYPlot = QtWidgets.QWidget(self.centralwidget)
        self.fftYPlot.setMinimumSize(QtCore.QSize(100, 100))
        self.fftYPlot.setStyleSheet("border-color: black;\n"
"border-width: 2px;\n"
"border-style: solid;")
        self.fftYPlot.setObjectName("fftYPlot")
        self.horizontalLayout_2.addWidget(self.fftYPlot)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.cameraControl = QtWidgets.QWidget(self.centralwidget)
        self.cameraControl.setMinimumSize(QtCore.QSize(100, 100))
        self.cameraControl.setStyleSheet("border-color: black;\n"
"border-width: 2px;\n"
"border-style: solid;")
        self.cameraControl.setObjectName("cameraControl")
        self.horizontalLayout_3.addWidget(self.cameraControl)
        self.statusInfo = QtWidgets.QWidget(self.centralwidget)
        self.statusInfo.setMinimumSize(QtCore.QSize(100, 100))
        self.statusInfo.setStyleSheet("border-color: black;\n"
"border-width: 2px;\n"
"border-style: solid;")
        self.statusInfo.setObjectName("statusInfo")
        self.horizontalLayout_3.addWidget(self.statusInfo)
        self.verticalLayout_2.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_4.addLayout(self.verticalLayout_2)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 350, 22))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuHelp = QtWidgets.QMenu(self.menubar)
        self.menuHelp.setObjectName("menuHelp")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionExit = QtWidgets.QAction(MainWindow)
        self.actionExit.setObjectName("actionExit")
        self.actionAbout = QtWidgets.QAction(MainWindow)
        self.actionAbout.setObjectName("actionAbout")
        self.menuFile.addAction(self.actionExit)
        self.menuHelp.addAction(self.actionAbout)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuHelp.setTitle(_translate("MainWindow", "Help"))
        self.actionExit.setText(_translate("MainWindow", "Exit"))
        self.actionExit.setToolTip(_translate("MainWindow", "Exit the Program"))
        self.actionExit.setShortcut(_translate("MainWindow", "Meta+Q"))
        self.actionAbout.setText(_translate("MainWindow", "About"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

