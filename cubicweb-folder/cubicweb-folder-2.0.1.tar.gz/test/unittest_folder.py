from cubicweb.devtools.testlib import CubicWebTC
from cubicweb_folder import views


class ClassifiableEntityTC(CubicWebTC):
    def setup_database(self):
        with self.admin_access.repo_cnx() as cnx:
            cnx.create_entity('Card', title=u"blah !")
            cnx.commit()

    def test_subject_filed_under_vocabulary(self):
        with self.admin_access.web_request() as req:
            r1 = req.create_entity('Folder', name=u"root1")
            req.create_entity('Folder', name=u"root2")
            c1 = req.create_entity('Folder', name=u"child1", filed_under=r1)
            itree_c1 = c1.cw_adapt_to('ITree')
            self.assertEqual([x.name
                              for x in itree_c1.iterparents()],
                             [u'root1'])
            self.assertEqual([x.name
                              for x in itree_c1.iterparents(strict=False)],
                             [u'child1', u'root1'])
            # on a new entity
            e = self.vreg['etypes'].etype_class('Card')(req)
            form = self.vreg['forms'].select('edition', req, entity=e)
            field = form.field_by_name('filed_under', 'subject',
                                       eschema=e.e_schema)
            folders = list(field.vocabulary(form))
            self.assertEqual(len(folders), 3)
            self.assertEqual(folders[0][0], u'root1')
            self.assertEqual(folders[1][0], u'root1 > child1')
            self.assertEqual(folders[2][0], u'root2')
            # on an existant unclassified entity
            e = req.execute('Any X WHERE X is Card').get_entity(0, 0)
            form = self.vreg['forms'].select('edition', req, entity=e)
            field = form.field_by_name('filed_under', 'subject',
                                       eschema=e.e_schema)
            folders = list(field.vocabulary(form))
            self.assertEqual(len(folders), 3)
            self.assertEqual(folders[0][0], u'root1')
            self.assertEqual(folders[1][0], u'root1 > child1')
            self.assertEqual(folders[2][0], u'root2')
            # on an existant classified entity
            req.execute('SET X filed_under Y '
                        'WHERE X eid %s, Y name "child1"' % e.eid)
            assert e.filed_under
            folders = list(field.vocabulary(form))
            self.assertEqual(len(folders), 3)
            self.assertEqual(folders[0][0], u'root1')
            self.assertEqual(folders[1][0], u'root1 > child1')
            self.assertEqual(folders[2][0], u'root2')
            # on an existant classified entity LIMIT SET
            folders = list(field.vocabulary(form, limit=10))
            self.assertEqual(len(folders), 2)
            self.assertEqual(folders[0][0], u'root1')
            self.assertEqual(folders[1][0], u'root2')
            # on an existant folder entity, don't propose itself and
            # descendants
            form = self.vreg['forms'].select('edition', req, entity=r1)
            field = form.field_by_name('filed_under', 'subject',
                                       eschema=e.e_schema)
            folders = list(field.vocabulary(form))
            self.assertEqual(len(folders), 1)
            self.assertEqual(folders[0][0], u'root2')

    def test_possible_views(self):
        with self.admin_access.web_request() as req:
            possibleviews = self.pviews(req, None)
            self.assertTrue(('tree', views.FolderTreeView) in possibleviews,
                            possibleviews)


if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
