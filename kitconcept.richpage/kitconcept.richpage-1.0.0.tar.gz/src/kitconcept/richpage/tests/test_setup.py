# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from kitconcept.richpage.testing import KITCONCEPT_RICHPAGE_INTEGRATION_TESTING  # noqa
from plone import api

import unittest


class TestSetup(unittest.TestCase):
    """Test that kitconcept.richpage is properly installed."""

    layer = KITCONCEPT_RICHPAGE_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if kitconcept.richpage is installed."""
        self.assertTrue(self.installer.isProductInstalled(
            'kitconcept.richpage'))

    def test_browserlayer(self):
        """Test that IKitconceptRichpageLayer is registered."""
        from kitconcept.richpage.interfaces import (
            IKitconceptRichpageLayer)
        from plone.browserlayer import utils
        self.assertIn(IKitconceptRichpageLayer, utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = KITCONCEPT_RICHPAGE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')
        self.installer.uninstallProducts(['kitconcept.richpage'])

    def test_product_uninstalled(self):
        """Test if kitconcept.richpage is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled(
            'kitconcept.richpage'))

    def test_browserlayer_removed(self):
        """Test that IKitconceptRichpageLayer is removed."""
        from kitconcept.richpage.interfaces import IKitconceptRichpageLayer
        from plone.browserlayer import utils
        self.assertNotIn(IKitconceptRichpageLayer, utils.registered_layers())
