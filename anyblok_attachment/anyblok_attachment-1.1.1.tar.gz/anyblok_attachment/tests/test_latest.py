# This file is a part of the AnyBlok / Attachment api project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from os import urandom

from anyblok.tests.testcase import DBTestCase
from anyblok_attachment.bloks.attachment.exceptions import NotLatestException


class TestFieldFunction(DBTestCase):
    blok_entry_points = ('bloks', 'test_bloks')

    def test_get_latest_document(self):
        registry = self.init_registry(None)
        registry.upgrade(install=('test_report_4',))
        file_ = urandom(100)
        doc = registry.Attachment.Document.insert(file=file_)
        t = registry.DocumentTest.insert()
        t.latest_document = doc
        self.assertEqual(t.latest_document.uuid, doc.uuid)
        self.assertEqual(t.latest_document.version, doc.version)
        doc.historize_a_copy()
        self.assertEqual(t.latest_document.uuid, doc.uuid)
        self.assertEqual(t.latest_document.version, doc.version)

    def test_del_latest_document(self):
        registry = self.init_registry(None)
        registry.upgrade(install=('test_report_4',))
        doc = registry.Attachment.Document.insert()
        t = registry.DocumentTest.insert(latest_document=doc)
        del t.latest_document
        self.assertEqual(t.latest_document_uuid, None)
        self.assertIsNone(t.latest_document)

    def test_check_latest_document(self):
        registry = self.init_registry(None)
        registry.upgrade(install=('test_report_4',))
        doc1 = registry.Attachment.Document.insert()
        registry.DocumentTest.insert(latest_document=doc1)
        doc2 = registry.Attachment.Document.insert()
        t2 = registry.DocumentTest.insert(latest_document=doc2)
        query = registry.DocumentTest.query()
        query = query.filter(registry.DocumentTest.is_latest_document(doc2))
        self.assertIs(query.one(), t2)

    def test_set_latest_document_with_versionned_document(self):
        registry = self.init_registry(None)
        registry.upgrade(install=('test_report_4',))
        file_ = urandom(100)
        doc = registry.Attachment.Document.insert(file=file_)
        t = registry.DocumentTest.insert()
        doc.historize_a_copy()
        with self.assertRaises(NotLatestException):
            t.latest_document = doc.previous_version

    def test_check_latest_document_with_versioned_document(self):
        registry = self.init_registry(None)
        registry.upgrade(install=('test_report_4',))
        file_ = urandom(100)
        doc = registry.Attachment.Document.insert(file=file_)
        registry.DocumentTest.insert(latest_document=doc)
        doc.historize_a_copy()
        query = registry.DocumentTest.query()
        with self.assertRaises(NotLatestException):
            query = query.filter(registry.DocumentTest.is_latest_document(
                doc.previous_version))
