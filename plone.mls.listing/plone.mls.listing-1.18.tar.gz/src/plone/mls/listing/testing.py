# -*- coding: utf-8 -*-
"""Test Layer for plone.mls.listing."""

# zope imports
from plone.app.testing import applyProfile
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer


class PloneMLSListing(PloneSandboxLayer):
    """Custom Test Layer for plone.mls.listing."""
    defaultBases = (PLONE_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        """Set up Zope for testing."""
        # Load ZCML
        import plone.mls.listing
        self.loadZCML(package=plone.mls.listing)

    def setUpPloneSite(self, portal):
        """Set up a Plone site for testing."""
        applyProfile(portal, 'plone.mls.listing:default')


PLONE_MLS_LISTING_FIXTURE = PloneMLSListing()
PLONE_MLS_LISTING_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PLONE_MLS_LISTING_FIXTURE, ),
    name='PloneMLSListing:Integration',
)
