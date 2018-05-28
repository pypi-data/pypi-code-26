# coding: utf-8

from os.path import join, dirname, isfile, exists
import shutil

from cubicweb.devtools.testlib import CubicWebTC

from cubicweb import NoSelectableObject, Binary, Unauthorized
from cubicweb.web import NotFound

from cubes.file.entities import thumb_cache_dir


class FileTC(CubicWebTC):
    icon = 'text.ico'
    mime_type = u"text/plain"

    def setup_database(self):
        with self.admin_access.repo_cnx() as cnx:
            create = cnx.create_entity
            self.fobj = create(
                'File', data_name=u"foo.pdf",
                data=Binary(b"xxx"),
                data_format=self.mime_type).eid
            self.ufobj = create(
                'File', data_name=u"Bâbâr.pdf",
                data=Binary(b"yyy"),
                data_format=self.mime_type).eid
            cnx.commit()

    def test_idownloadable(self):
        with self.admin_access.client_cnx() as cnx:
            fobj = cnx.entity_from_eid(self.fobj)
            idownloadable = fobj.cw_adapt_to('IDownloadable')
            self.assertEqual(idownloadable.download_data(), b'xxx')
            self.assertEqual(idownloadable.download_url(),
                             u'http://testing.fr/cubicweb/%s/%s/raw/%s' % (
                fobj.__regid__.lower(), self.fobj, fobj.data_name))
            self.assertEqual(
                idownloadable.download_content_type(),
                self.mime_type)

    def test_idownloadable_unicode(self):
        with self.admin_access.client_cnx() as cnx:
            ufobj = cnx.entity_from_eid(self.ufobj)
            idownloadable = ufobj.cw_adapt_to('IDownloadable')
            self.assertEqual(
                idownloadable.download_url(),
                u'http://testing.fr/cubicweb/%s/%s/raw/%s'
                % (ufobj.__regid__.lower(),
                   self.ufobj,
                   ufobj.data_name.replace(u'â', '%C3%A2')))

    def test_base(self):
        with self.admin_access.web_request() as req:
            fobj = req.entity_from_eid(self.fobj)
            self.assertEqual(fobj.size(), 3)
            self.assertEqual(
                fobj.icon_url(),
                'http://testing.fr/cubicweb/data/icons/'+self.icon)

    def test_views(self):
        with self.admin_access.web_request() as req:
            fobj = req.entity_from_eid(self.fobj)
            self.vreg['views'].select('download', req, rset=fobj.cw_rset)
            fobj.view('gallery')
            self.assertRaises(NoSelectableObject, fobj.view, 'image')
            self.assertRaises(NoSelectableObject, fobj.view, 'album')

    def test_sha1hex(self):
        with self.admin_access.client_cnx() as cnx:
            self.create_user(cnx, login=u'simpleuser')
            cnx.commit()
        with self.new_access(u'simpleuser').client_cnx() as cnx:
            cnx.vreg.config['compute-sha1hex'] = 1
            obj = cnx.create_entity('File', data_name=u"myfile.pdf",
                                    data=Binary(b"xxx"),
                                    data_format=self.mime_type)
            cnx.commit()
            self.assertEqual(
                'b60d121b438a380c343d5ec3c2037564b82ffef3',
                obj.compute_sha1hex())
            self.assertEqual(
                'b60d121b438a380c343d5ec3c2037564b82ffef3',
                obj.data_sha1hex)  # can read
            with self.assertRaises(Unauthorized):
                # write is forbiden
                obj.cw_set(data_sha1hex=u'1234')
                cnx.commit()
            obj.cw_set(data=Binary(b'zzz'))
            obj.cw_clear_all_caches()
            self.assertEqual(
                '40fa37ec00c761c7dbb6ebdee6d4a260b922f5f4',
                obj.data_sha1hex)
            with self.assertRaises(Unauthorized):
                cnx.create_entity('File', data_name=u'anotherfile.pdf',
                                  data=Binary(b'yyy'),
                                  data_format=self.mime_type,
                                  data_sha1hex=u'deadbeef')
                cnx.commit()

    def test_sha1hex_nodata(self):
        with self.admin_access.client_cnx() as cnx:
            with cnx.deny_all_hooks_but('metadata'):
                cnx.vreg.config['compute-sha1hex'] = 1
                obj = cnx.create_entity('File')
                cnx.commit()
            self.assertEqual(None, obj.data)
            self.assertEqual(None, obj.data_sha1hex)
            self.assertEqual(None, obj.compute_sha1hex())


class ImageTC(CubicWebTC):
    icon = 'image_png.ico'
    mime_type = u"image/png"

    @property
    def data(self):
        with open(join(dirname(__file__), 'data', '20x20.gif'), 'rb') as fobj:
            return fobj.read()

    def setUp(self):
        super(ImageTC, self).setUp()
        cachedir = thumb_cache_dir(self.repo.vreg.config)
        if exists(cachedir):
            shutil.rmtree(cachedir)
        self.cachedir = cachedir

    def tearDown(self):
        super(ImageTC, self).tearDown()
        if exists(self.cachedir):
            shutil.rmtree(self.cachedir)

    def setup_database(self):
        with self.admin_access.repo_cnx() as cnx:
            create = cnx.create_entity
            self.fobj = create(
                'File', data_name=u"foo.gif", data=Binary(b"xxx"),
                data_format=self.mime_type).eid
            self.ufobj = create(
                'File', data_name=u"Bâbâr.png",
                data=Binary(b"yyy"),
                data_format=self.mime_type).eid
            cnx.commit()

    def test_views(self):
        with self.admin_access.web_request() as req:
            fobj = req.entity_from_eid(self.fobj)
            self.vreg['views'].select('download', req, rset=fobj.cw_rset)
            fobj.view('gallery')
            fobj.view('image')
            fobj.view('album')
        with self.admin_access.web_request(selected='something stupid') as req:
            fobj = req.entity_from_eid(self.fobj)
            with self.assertRaises(NotFound):
                req.view('gallery', fobj.cw_rset)
        with self.admin_access.web_request(selected='6666') as req:
            fobj = req.entity_from_eid(self.fobj)
            with self.assertRaises(NotFound):
                req.view('gallery', fobj.cw_rset)

    def test_thumbnail_generation_fails(self):
        with self.admin_access.web_request() as req:
            fobj = req.entity_from_eid(self.fobj)
            ithumb = fobj.cw_adapt_to('IThumbnail')
            # the actual thumbnail generation fails because the actual
            # file content is (literally) "xxx"
            self.assertEqual(ithumb.thumbnail_data(), '')
            self.assertEqual(
                u'http://testing.fr/cubicweb/%s/%s/thumb/foo_75x75.png' %
                (fobj.__regid__.lower(), self.fobj),
                ithumb.thumbnail_url())

    def test_thumbnail(self):
        with self.admin_access.client_cnx() as cnx:
            img = cnx.create_entity(
                'File', data=Binary(self.data),
                data_name=u'20x20.gif')
            cnx.commit()
            thumbadapter = img.cw_adapt_to('IThumbnail')
            self.assertEqual(
                '20x20_75x75.png',
                thumbadapter.thumbnail_file_name())
            self.assertEqual(
                'http://testing.fr/cubicweb/file/%s/thumb/20x20_75x75.png' % img.eid,  # noqa
                thumbadapter.thumbnail_url())
            cachepath = thumbadapter._thumbnail_path()
            self.assertIsNone(thumbadapter.thumbnail_path())
            self.assertFalse(isfile(cachepath))

            img = cnx.execute(
                'File F WHERE F data_name="20x20.gif"').get_entity(0, 0)
            thumbadapter = img.cw_adapt_to('IThumbnail')
            self.assertTrue(thumbadapter.thumbnail_data())
            cachepath = thumbadapter.thumbnail_path()
            self.assertTrue(isfile(cachepath))
            self.assertEqual(open(cachepath, 'rb').read(),
                             thumbadapter.thumbnail_data())


class MimeTypeDetectionTC(CubicWebTC):

    def test_extra_dot(self):
        with self.admin_access.client_cnx() as cnx:
            fobj = cnx.create_entity('File', data_name=u"foo.toto.pdf",
                                     data=Binary(b"xxx"))
            self.assertEqual(fobj.data_format, 'application/pdf')

    def test_file_name_priority(self):
        with self.admin_access.web_request() as req:
            req.form = {
                'eid': ['X'],
                '__maineid': 'X',
                '__type:X': 'File',
                '_cw_entity_fields:X': 'data-subject,data_name-subject',
                'data-subject:X': (u'coucou.txt', Binary(b'coucou')),
                'data_name-subject:X': u'coco.txt',
            }
            path, params = self.expect_redirect_handle_request(req, 'edit')
            self.assertTrue(path.startswith('file/'), path)
            eid = path.split('/')[1]
            efile = req.entity_from_eid(eid)
            self.assertEqual(efile.data_name, 'coco.txt')


if __name__ == '__main__':
    from unittest import main
    main()
