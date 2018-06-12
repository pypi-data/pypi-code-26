#! python
# -*- coding: utf-8 -*-


"""Module for pulse sequence related classes and functions.

Authors:
    * Victor Hugo de Mello Pessoa <victor.pessoa@usp.br>
    * Daniel Cosmo Pizetta <daniel.pizetta@usp.br>

Since:
    2017/07/01

"""

import logging

import numpy as np
import pyqtgraph.parametertree as pt

from mrsprint.system import gradient, rf

_logger = logging.getLogger(__name__)


class Sequence(pt.parameterTypes.GroupParameter):
    """Class that represents a sequence for magnetic resonance systems."""

    def __init__(self, settings, **opts):
        opts['name'] = 'Sequence'
        opts['type'] = 'bool'
        opts['value'] = True
        pt.parameterTypes.GroupParameter.__init__(self, **opts)

        self.settings = settings
        dt = settings.simulator_group.timeResolution.value()
        self.__rf = rf.rfDelay(dt)
        self.__gradient = gradient.gradientDelay(dt)

    def setRF(self, rf):
        """Properly sets the rf stream signal."""
        for rep_num, events in rf:
            for _ in np.arange(0, rep_num):
                for event in events:
                    self.__rf = np.append(self.__rf, event)

    def getRF(self):
        """Return the entire rf."""
        return self.__rf

    def setGradient(self, gradient):
        """Properly sets the gradient."""
        for rep_num, events in gradient:
            for _ in np.arange(0, rep_num):
                for event in events:
                    self.__gradient = np.append(self.__gradient, event)

    def getGradient(self):
        """Return the entire gradient."""
        rf_shape = self.__rf.shape
        gradient_size = self.__gradient.size

        grad_zero = np.zeros(3 * (rf_shape[0])).reshape(3, rf_shape[0])

        if 3 * rf_shape[0] != gradient_size:
            if gradient_size <= 3:
                self.__gradient = grad_zero
            else:
                raise ValueError("RF and Gradient must have the same temporal size!")
        return self.__gradient


class CPMGSequence(Sequence):
    """Generates a CPMG sequence."""

    def __init__(self):
        Sequence.__init__(self)
        # sequence specific parameters

        self.numberOfCicles = self.addChild({'name': 'Number of Cicles', 'type': 'int', 'value': 3})
        self.te = self.addChild({'name': 'Time to Echo', 'type': 'float', 'value': 0.02, 'suffix': 's', 'siPrefix': True})
        self.dtr = self.addChild({'name': 'Delay TR', 'type': 'float', 'value': 0.02, 'suffix': 's', 'siPrefix': True})

        # pulse of 90 degrees in x
        rf_90_x = rf.squareRFPulse(flip_angle=90, phase=0)
        t_half_rf_90 = rf.rfDuration(rf_90_x) / 2.
        # pulse of 180 degrees in y
        rf_180_y = rf.squareRFPulse(flip_angle=180, phase=90)
        t_half_rf_180 = rf.rfDuration(rf_180_y) / 2.

        # delay bewteen pulse 90x and 180y  = te/2 between pulse centers
        d_90_180 = rf.rfDelay(-t_half_rf_90 + self.te.value() / 2. - t_half_rf_180)
        # delay bewteen pulse 180y and 180y  = te between pulse centers
        d_180_180 = rf.rfDelay(-t_half_rf_180 + self.te.value() - t_half_rf_180)
        # delay repetition time before reinitiates
        d_tr = rf.rfDelay(self.dtr.value())

        # rf for CPMG
        self.setRF([(1, [rf_90_x, d_90_180]),
                    (self.numberOfCicles.value(), [-rf_180_y, d_180_180, rf_180_y, d_180_180]),
                    (1, [d_tr])])


class GradientEchoSequence(Sequence):
    """Generate a Gradient Echo sequence."""

    def __init__(self):
        Sequence.__init__(self)
        # sequence specific parameters
        self.a90 = self.addChild({'name': 'Delay After RF', 'type': 'float', 'value': 0.01, 'suffix': 's', 'siPrefix': True})
        self.te = self.addChild({'name': 'Time to Echo', 'type': 'float', 'value': 0.02, 'suffix': 's', 'siPrefix': True})
        self.dtr = self.addChild({'name': 'Delay TR', 'type': 'float', 'value': 0.01, 'suffix': 's', 'siPrefix': True})

        # first event, excitation
        rf_90_x = rf.squareRFPulse(flip_angle=90, phase=0)
        t_rf_90 = rf.rfDuration(rf_90_x)
        d_gr_90 = gradient.gradientDelay(t_rf_90)

        # second event, a delay
        d_rf_a90 = rf.rfDelay(self.dbgr.value())
        d_gr_a90 = gradient.gradientDelay(self.dbgr.value())

        # third event, dephasing
        d_rf_deph = rf.rfDelay()
        gr_deph = gradient.SquareGradient()

        # fourth event, read
        d_rf_read = rf.rfDelay()
        gr_read = gradient.SquareGradient()

        # fifty event, a delay
        d_rf_tr = rf.rfDelay(self.dtr.value())
        d_gr_tr = gradient.gradientDelay(self.dtr.value())

        self.setRF([(1, [rf_90_x, d_rf_a90, d_rf_deph, d_rf_read, d_rf_tr])])
        self.setGradient([(1, [d_gr_90, d_gr_a90, gr_deph, gr_read, d_gr_tr])])
