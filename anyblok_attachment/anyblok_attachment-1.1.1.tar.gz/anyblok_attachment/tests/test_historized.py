# This file is a part of the AnyBlok / Attachment api project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from os import urandom

from anyblok.tests.testcase import DBTestCase


class TestFieldFunction(DBTestCase):
    blok_entry_points = ('bloks', 'test_bloks')

    def test_get_versioned_document(self):
        registry = self.init_registry(None)
        registry.upgrade(install=('test_report_4',))
        file_ = urandom(100)
        doc = registry.Attachment.Document.insert(file=file_)
        t = registry.DocumentTest2.insert(versioned_document=doc)
        self.assertEqual(doc.version, t.versioned_document.version)
        doc.historize_a_copy()
        self.assertNotEqual(doc.version, t.versioned_document.version)

    def test_del_versioned_document(self):
        registry = self.init_registry(None)
        registry.upgrade(install=('test_report_4',))
        doc = registry.Attachment.Document.insert()
        t = registry.DocumentTest2.insert(versioned_document=doc)
        del t.versioned_document
        self.assertEqual(t.versioned_document_uuid, None)
        self.assertEqual(t.versioned_document_version, None)
        self.assertIsNone(t.versioned_document)

    def test_check_versioned_document(self):
        registry = self.init_registry(None)
        registry.upgrade(install=('test_report_4',))
        doc1 = registry.Attachment.Document.insert()
        registry.DocumentTest2.insert(versioned_document=doc1)
        doc2 = registry.Attachment.Document.insert()
        t2 = registry.DocumentTest2.insert(versioned_document=doc2)
        query = registry.DocumentTest2.query()
        query = query.filter(registry.DocumentTest2.is_versioned_document(doc2))
        self.assertIs(query.one(), t2)
