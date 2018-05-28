# This file is part of Sympathy for Data.
# Copyright (c) 2013 System Engineering Software Society
#
# Sympathy for Data is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Sympathy for Data is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sympathy for Data.  If not, see <http://www.gnu.org/licenses/>.
import PySide.QtCore as QtCore
import functools


class SignalMuxer(QtCore.QObject):

    """
    This class emits "triggered" when all defined incoming signals have been
    triggered.
    """
    triggered = QtCore.Signal()

    def __init__(self, parent=None):
        super(SignalMuxer, self).__init__(parent)

        self._incoming = {}
        self._triggered = []

    def add_signal(self, signal):
        self._incoming[signal] = False
        signal.connect(functools.partial(self.incoming, signal))

    @QtCore.Slot(QtCore.QObject)
    def incoming(self, signal):
        self._incoming[signal] = True
        if not False in self._incoming.values():
            self.triggered.emit()
