
from cubicweb import ValidationError
from cubicweb.devtools.testlib import CubicWebTC


class HooksTC(CubicWebTC):

    def setup_database(self):
        with self.admin_access.repo_cnx() as cnx:
            self.foldr = cnx.create_entity(u'Folder', name=u'xyz').eid
            self.foldr2 = cnx.create_entity(u'Folder', name=u'xyz2').eid
            cnx.commit()

    def test_folder_no_conflict(self):
        with self.admin_access.repo_cnx() as cnx:
            cnx.execute(u'INSERT Folder F: F name "foo", F filed_under PF '
                        u'WHERE PF eid %(x)s', {'x': self.foldr})[0][0]
            cnx.execute(u'INSERT Folder F: F name "foo", F filed_under PF '
                        u'WHERE PF eid %(x)s', {'x': self.foldr2})[0][0]
            cnx.commit()

    def test_folder_insertion_with_name_conflict(self):
        with self.admin_access.repo_cnx() as cnx:
            cnx.execute(u'INSERT Folder F: F name "foo", F filed_under PF '
                        u'WHERE PF eid %(x)s', {'x': self.foldr})
            cnx.commit()
            self.assertRaises(ValidationError, cnx.execute,
                              u'INSERT Folder F: F name "foo", '
                              u'F filed_under PF '
                              u'WHERE PF eid %(x)s', {'x': self.foldr})

    def test_folder_update_with_name_conflict(self):
        with self.admin_access.repo_cnx() as cnx:
            cnx.execute(u'INSERT Folder F: F name "foo", '
                        u'F filed_under PF '
                        u'WHERE PF eid %(x)s', {'x': self.foldr})
            wp2 = cnx.execute(u'INSERT Folder F: F name "foo2", '
                              u'F filed_under PF '
                              u'WHERE PF eid %(x)s', {'x': self.foldr})[0][0]
            cnx.commit()
            self.assertRaises(ValidationError, cnx.execute,
                              u'SET X name "foo" WHERE X eid %s' % wp2)

    def test_folder_description_update(self):
        """checks that we can update a F's description
        without having a UNIQUE violation error
        """
        with self.admin_access.repo_cnx() as cnx:
            cnx.execute(u'INSERT Folder F: F name "foo", '
                        u'F filed_under PF '
                        u'WHERE PF eid %(x)s', {'x': self.foldr})[0][0]
            wp2 = cnx.execute(u'INSERT Folder F: F name "foo2", '
                              u'F filed_under PF '
                              u'WHERE PF eid %(x)s', {'x': self.foldr})[0][0]
            cnx.commit()
            # we should be able to update description only
            cnx.execute('SET X description "foo" WHERE X eid %s' % wp2)


if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
