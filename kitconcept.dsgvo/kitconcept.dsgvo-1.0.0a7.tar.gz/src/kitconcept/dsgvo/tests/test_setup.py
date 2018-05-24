# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from kitconcept.dsgvo.testing import KITCONCEPT_DSGVO_INTEGRATION_TESTING  # noqa
from plone import api

import unittest


class TestSetup(unittest.TestCase):
    """Test that kitconcept.dsgvo is properly installed."""

    layer = KITCONCEPT_DSGVO_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if kitconcept.dsgvo is installed."""
        self.assertTrue(self.installer.isProductInstalled(
            'kitconcept.dsgvo'))

    def test_browserlayer(self):
        """Test that IKitconceptDsgvoLayer is registered."""
        from kitconcept.dsgvo.interfaces import (
            IKitconceptDsgvoLayer)
        from plone.browserlayer import utils
        self.assertIn(IKitconceptDsgvoLayer, utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = KITCONCEPT_DSGVO_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')
        self.installer.uninstallProducts(['kitconcept.dsgvo'])

    def test_product_uninstalled(self):
        """Test if kitconcept.dsgvo is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled(
            'kitconcept.dsgvo'))

    def test_browserlayer_removed(self):
        """Test that IKitconceptDsgvoLayer is removed."""
        from kitconcept.dsgvo.interfaces import IKitconceptDsgvoLayer
        from plone.browserlayer import utils
        self.assertNotIn(IKitconceptDsgvoLayer, utils.registered_layers())
