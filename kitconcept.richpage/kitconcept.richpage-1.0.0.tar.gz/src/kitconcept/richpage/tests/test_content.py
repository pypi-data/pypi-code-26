# -*- coding: utf-8 -*-
from kitconcept.richpage.content.audio import IAudio
from kitconcept.richpage.content.googlemap import IGoogleMap
from kitconcept.richpage.content.image import IImage
from kitconcept.richpage.content.file import IFile
from kitconcept.richpage.content.richpage import IRichPage
from kitconcept.richpage.content.slideshow import ISlideshow
from kitconcept.richpage.content.text import IText
from kitconcept.richpage.content.video import IVideo
from kitconcept.richpage.testing import KITCONCEPT_RICHPAGE_INTEGRATION_TESTING  # noqa
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.dexterity.interfaces import IDexterityFTI
from zope.component import createObject
from zope.component import queryUtility

import unittest


class ContentIntegrationTest(unittest.TestCase):

    layer = KITCONCEPT_RICHPAGE_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def add_richpage(self):
        self.portal.invokeFactory('RichPage', 'RichPage')

    def test_schema(self):
        fti = queryUtility(IDexterityFTI, name='RichPage')
        schema = fti.lookupSchema()
        self.assertEqual(IRichPage, schema)

    def test_fti(self):
        fti = queryUtility(IDexterityFTI, name='RichPage')
        self.assertTrue(fti)

    def test_factory(self):
        fti = queryUtility(IDexterityFTI, name='RichPage')
        factory = fti.factory
        obj = createObject(factory)
        self.assertTrue(IRichPage.providedBy(obj))

    def test_adding_richpage(self):
        self.portal.invokeFactory('RichPage', 'RichPage')
        self.assertTrue(
            IRichPage.providedBy(self.portal['RichPage'])
        )

    def test_richpage_adding_text(self):
        self.add_richpage()
        self.portal['RichPage'].invokeFactory('RichPageText', 'RichPageText')
        self.assertTrue(
            IText.providedBy(self.portal['RichPage']['RichPageText']))

    def test_richpage_adding_image(self):
        self.add_richpage()
        self.portal['RichPage'].invokeFactory('RichPageImage', 'RichPageImage')
        self.assertTrue(
            IImage.providedBy(self.portal['RichPage']['RichPageImage']))

    def test_richpage_adding_file(self):
        self.add_richpage()
        self.portal['RichPage'].invokeFactory('RichPageFile', 'RichPageFile')
        self.assertTrue(
            IFile.providedBy(self.portal['RichPage']['RichPageFile']))

    def test_richpage_adding_audio(self):
        self.add_richpage()
        self.portal['RichPage'].invokeFactory('Audio', 'Audio')
        self.assertTrue(
            IAudio.providedBy(self.portal['RichPage']['Audio']))

    def test_richpage_adding_video(self):
        self.add_richpage()
        self.portal['RichPage'].invokeFactory('Video', 'Video')
        self.assertTrue(
            IVideo.providedBy(self.portal['RichPage']['Video']))

    def test_richpage_adding_googlemap(self):
        self.add_richpage()
        self.portal['RichPage'].invokeFactory('GoogleMap', 'GoogleMap')
        self.assertTrue(
            IGoogleMap.providedBy(self.portal['RichPage']['GoogleMap']))

    def test_richpage_adding_slideshow(self):
        self.add_richpage()
        self.portal['RichPage'].invokeFactory('Slideshow', 'Slideshow')
        self.assertTrue(
            ISlideshow.providedBy(self.portal['RichPage']['Slideshow']))
