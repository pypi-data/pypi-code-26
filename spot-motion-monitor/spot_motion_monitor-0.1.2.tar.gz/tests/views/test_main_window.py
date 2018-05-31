#------------------------------------------------------------------------------
# Copyright (c) 2018 LSST Systems Engineering
# Distributed under the MIT License. See LICENSE for more information.
#------------------------------------------------------------------------------
from unittest import mock

from PyQt5.QtWidgets import QAction, QMainWindow

from spot_motion_monitor.views.main_window import SpotMotionMonitor

class TestMainWindow():

    def test_main_window_exit(self, qtbot):
        with mock.patch.object(QMainWindow, 'close') as mock_method:
            mw = SpotMotionMonitor()
            mw.show()
            qtbot.addWidget(mw)
            mw.actionExit.trigger()
            assert mock_method.call_count == 1

    def test_main_window_about(self, qtbot):
        with mock.patch.object(SpotMotionMonitor, 'about') as mock_method:
            mw = SpotMotionMonitor()
            mw.show()
            qtbot.addWidget(mw)
            mw.actionAbout.trigger()
            assert mock_method.call_count == 1

    def test_set_action_icon(self, qtbot):
        mw = SpotMotionMonitor()
        qtbot.addWidget(mw)
        action = QAction()
        mw.set_action_icon(action, "test.png", True)
        assert action.icon() is not None
        assert action.isIconVisibleInMenu() is True
