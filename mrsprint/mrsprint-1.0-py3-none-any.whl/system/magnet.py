#! python
# -*- coding: utf-8 -*-

"""Module for magnet related classes and functions.

Authors:
    * Victor Hugo de Mello Pessoa <victor.pessoa@usp.br>
    * Daniel Cosmo Pizetta <daniel.pizetta@usp.br>

Since:
    2017/07/01

Todo:
    Maybe put all config together in magnet classes.

"""

import logging

import pyqtgraph.parametertree as pt

_logger = logging.getLogger(__name__)


class MagnetConfig(pt.parameterTypes.GroupParameter):
    """Class that configure the limit parameters of the magnet."""

    def __init__(self, **opts):
        opts['name'] = 'Magnet Config'
        opts['type'] = 'bool'
        opts['value'] = True
        pt.parameterTypes.GroupParameter.__init__(self, **opts)
        self.maxMagneticStrength = self.addChild({'name': 'Max Magnetic Strength', 'type': 'float', 'value': 5, 'suffix': 'T', 'siPrefix': True, 'limits': (0., 20.)})
        self.SizeX = self.addChild({'name': 'Size X', 'type': 'float', 'value': 20.0, 'suffix': ' cm', 'limits': (0., 100.)})
        self.SizeY = self.addChild({'name': 'Size Y', 'type': 'float', 'value': 20.0, 'suffix': ' cm', 'limits': (0., 100.)})
        self.SizeZ = self.addChild({'name': 'Size Z', 'type': 'float', 'value': 60.0, 'suffix': ' cm', 'limits': (0., 100.)})


class Magnet(pt.parameterTypes.GroupParameter):
    """Class that represents the parameters in the magnet.

    Args:
        magnet_config (MagnetConfig): An object that represents the limits to this magnet.

    """

    def __init__(self, magnet_config, **opts):
        opts['name'] = 'Magnet'
        opts['type'] = 'bool'
        opts['value'] = True
        pt.parameterTypes.GroupParameter.__init__(self, **opts)
        self.magneticStrength = self.addChild({'name': 'Magnetic Strength', 'type': 'float', 'value': 3, 'suffix': 'T', 'siPrefix': True})
        self.magneticStrength.setLimits((0., magnet_config.maxMagneticStrength.value()))
        self.carrierFrequency = self.addChild({'name': 'Carrier Frequency', 'type': 'float', 'value': 127.728, 'suffix': 'MHz', 'siPrefix': True, 'readonly': True})


class Resolution(pt.parameterTypes.GroupParameter):
    """Class that represents the parameters of field inhomogeneity set to the data.

    Todo:
        This class needs to be reviewed for its parameters.

    """

    def __init__(self, **opts):
        opts['name'] = 'Field Inhomogeneity Resolution'
        opts['type'] = 'bool'
        opts['value'] = True
        pt.parameterTypes.GroupParameter.__init__(self, **opts)

        # Number of points in each direction
        self.N = self.addChild({'name': 'N', 'values': [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024], 'value': 2, 'type': 'list'})


class InhomogeneityConfig(pt.parameterTypes.GroupParameter):
    """Class that configure the limit parameters of each field inhomogeneity element.

    Todo:
        This class needs to be reviewed for its parameters.

    """

    def __init__(self, **opts):
        opts['name'] = 'Field Inhomogeneity Config'
        opts['type'] = 'bool'
        opts['value'] = True
        pt.parameterTypes.GroupParameter.__init__(self, **opts)

        # B0x Limits and Default
        self.limitB0x = self.addChild({'name': 'B0x Limit Value', 'type': 'float', 'value': 10., 'step': 1, 'limits': (0, 100), 'suffix': ' mT', 'siPrefix': True})
        self.B0x = self.addChild({'name': 'B0x Default', 'type': 'float', 'value': 0., 'step': 1, 'limits': (-100, 100), 'suffix': ' mT', 'siPrefix': True})

        # B0y Limits and Default
        self.limitB0y = self.addChild({'name': 'B0y Limit Value', 'type': 'float', 'value': 10., 'step': 1, 'limits': (0, 100), 'suffix': ' mT', 'siPrefix': True})
        self.B0y = self.addChild({'name': 'B0y Default', 'type': 'float', 'value': 0., 'step': 1, 'limits': (-100, 100), 'suffix': ' mT', 'siPrefix': True})

        # B0z Limits and Default
        self.limitB0z = self.addChild({'name': 'B0z Limit Value', 'type': 'float', 'value': 10., 'step': 1, 'limits': (0, 100), 'suffix': ' mT', 'siPrefix': True})
        self.B0z = self.addChild({'name': 'B0z Default', 'type': 'float', 'value': 0., 'step': 1, 'limits': (-100, 100), 'suffix': ' mT', 'siPrefix': True})


class Inhomogeneity(pt.parameterTypes.GroupParameter):
    """Class that represents the parameters of each field inhomogeneity element.

    Args:
        inhomogeneity_config (InhomogeneityConfig): An object that represents the
            limits to the field inhomogeneity element

    Todo:
        This class needs to be reviewed for its parameters.

    """

    def __init__(self, inhomogeneity_config, **opts):
        opts['name'] = 'Field Inhomogeneity'
        opts['type'] = 'bool'
        opts['value'] = True
        pt.parameterTypes.GroupParameter.__init__(self, **opts)

        # B0x, B0y and B0z
        self.B0x = self.addChild({'name': 'B0x', 'type': 'float', 'value': 0., 'step': 1, 'limits': (-100, 100), 'suffix': ' mT', 'siPrefix': True})
        self.B0x.setValue(inhomogeneity_config.B0x.value())
        self.B0x.setLimits((- inhomogeneity_config.limitB0x.value(), inhomogeneity_config.limitB0x.value()))

        self.B0y = self.addChild({'name': 'B0y', 'type': 'float', 'value': 0., 'step': 1, 'limits': (-100, 100), 'suffix': ' mT', 'siPrefix': True})
        self.B0y.setValue(inhomogeneity_config.B0y.value())
        self.B0y.setLimits((- inhomogeneity_config.limitB0y.value(), inhomogeneity_config.limitB0y.value()))

        self.B0z = self.addChild({'name': 'B0z', 'type': 'float', 'value': 0., 'step': 1, 'limits': (-100, 100), 'suffix': ' mT', 'siPrefix': True})
        self.B0z.setValue(inhomogeneity_config.B0z.value())
        self.B0z.setLimits((- inhomogeneity_config.limitB0z.value(), inhomogeneity_config.limitB0z.value()))
