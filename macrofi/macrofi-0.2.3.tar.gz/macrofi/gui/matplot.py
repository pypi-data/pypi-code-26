import numpy
import random
from PyQt5.QtWidgets import QSizePolicy
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from qtpy import QtCore, QtWidgets
from scipy import interpolate

from macrofi.gui import Ui_mainWindow


class PlotCanvas(
    FigureCanvas):  # 通过继承FigureCanvas类，使得该类既是一个PyQt5的Qwidget，又是一个matplotlib的FigureCanvas，这是连接pyqt5与matplotlib的关键

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height),
                     dpi=dpi)  # 创建一个Figure，注意：该Figure为matplotlib下的figure，不是matplotlib.pyplot下面的figure
        self.axes = fig.add_subplot(111)  # 调用figure下面的add_subplot方法，类似于matplotlib.pyplot下面的subplot方法

        FigureCanvas.__init__(self, fig)  # 初始化父类
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.plot()

    def plot(self):
        data = [random.random() for i in range(25)]
        ax = self.figure.add_subplot(111)
        ax.plot(data, 'r-')
        ax.set_title('PyQt Matplotlib Example')
        self.draw()


import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QVBoxLayout, QSizePolicy, QMessageBox, QWidget, \
    QPushButton
from PyQt5.QtGui import QIcon

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

import random


class App(QMainWindow):

    def __init__(self):
        super().__init__()
        self.left = 10
        self.top = 10
        self.title = 'PyQt5 matplotlib example - pythonspot.com'
        self.width = 640
        self.height = 400
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        m = PlotCanvas(self, width=5, height=4)
        m.move(0, 0)

        button = QPushButton('PyQt5 button', self)
        button.setToolTip('This s an example button')
        button.move(500, 0)
        button.resize(140, 100)

        self.show()


class PlotCanvas(FigureCanvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.plot()

    def plot(self):
        data = [random.random() for i in range(25)]
        ax = self.figure.add_subplot(111)
        ax.plot(data, 'r-')
        ax.set_title('PyQt Matplotlib Example')
        self.draw()


class PlotCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)  # 调用figure下面的add_subplot方法，类似于matplotlib.pyplot下面的subplot方法
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self,
                                   QtWidgets.QSizePolicy.Expanding,
                                   QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.test()

    def test(self):
        self.init_plot()
        # 每秒更新一次图像
        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.update_figure)
        timer.start(1000)

    def init_plot(self):
        x = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        y = [23, 21, 32, 13, 3, 132, 13, 3, 1]
        self.axes.plot(x, y)

    def update_figure(self, x, y):
        x = numpy.linspace(0, 10, 10)
        y = [random.randint(0, 10) for i in range(10)]
        xx = numpy.linspace(0, 10)
        f = interpolate.interp1d(x, y, 'quadratic')  # 产生插值曲线的函数
        yy = f(xx)
        self.axes.cla()
        self.axes.plot(x, y, 'o', xx, yy)
        self.draw()


def matplot_start():
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
