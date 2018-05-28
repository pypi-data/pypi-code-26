# -*- coding: utf-8 -*-

from os.path import join, dirname
from PIL.Image import open as pilopen

from cubicweb import Binary, Unauthorized
from cubicweb.devtools.testlib import CubicWebTC


class FileTC(CubicWebTC):

    def test_set_mime_and_encoding(self):
        with self.admin_access.client_cnx() as cnx:
            fobj = cnx.create_entity(
                'File', data_name=u"foo.txt", data=Binary(b"xxx"))
            self.assertEqual(fobj.data_format, u'text/plain')
            self.assertEqual(fobj.data_encoding, cnx.encoding)

    def test_set_mime_and_encoding_gz_file(self):
        with self.admin_access.client_cnx() as cnx:
            fobj = cnx.create_entity(
                'File', data_name=u"foo.txt.gz", data=Binary(b"xxx"))
            self.assertEqual(fobj.data_format, u'text/plain')
            self.assertEqual(fobj.data_encoding, u'gzip')
            fobj = cnx.create_entity(
                'File', data_name=u"foo.txt.gz", data=Binary(b"xxx"),
                data_format='application/gzip')
            self.assertEqual(fobj.data_format, u'text/plain')
            self.assertEqual(fobj.data_encoding, u'gzip')
            fobj = cnx.create_entity(
                'File', data_name=u"foo.gz", data=Binary(b"xxx"))
            self.assertEqual(fobj.data_format, u'application/gzip')
            self.assertEqual(fobj.data_encoding, None)

    def test_set_mime_and_encoding_bz2_file(self):
        with self.admin_access.client_cnx() as cnx:
            fobj = cnx.create_entity(
                'File', data_name=u"foo.txt.bz2", data=Binary(b"xxx"))
            self.assertEqual(fobj.data_format, u'text/plain')
            self.assertEqual(fobj.data_encoding, u'bzip2')
            fobj = cnx.create_entity(
                'File', data_name=u"foo.txt.bz2", data=Binary(b"xxx"),
                data_format='application/bzip2')
            self.assertEqual(fobj.data_format, u'text/plain')
            self.assertEqual(fobj.data_encoding, u'bzip2')
            fobj = cnx.create_entity(
                'File', data_name=u"foo.bz2", data=Binary(b"xxx"))
            self.assertEqual(fobj.data_format, u'application/bzip2')
            self.assertEqual(fobj.data_encoding, None)

    def test_set_mime_and_encoding_unknwon_ext(self):
        with self.admin_access.client_cnx() as cnx:
            fobj = cnx.create_entity(
                'File', data_name=u"foo.123", data=Binary(b"xxx"))
            self.assertEqual(fobj.data_format, u'application/octet-stream')
            self.assertEqual(fobj.data_encoding, None)


class ImageTC(CubicWebTC):

    @property
    def data(self):
        with open(join(dirname(__file__), 'data', '20x20.gif'), 'rb') as fobj:
            return fobj.read()

    def test_resize_image(self):
        with self.admin_access.client_cnx() as cnx:
            # check no resize
            img = cnx.create_entity(
                'File', data=Binary(self.data), data_name=u'20x20.gif')
            self.assertEqual(img.data_format, u'image/gif')
            self.assertEqual(img.data.getvalue(), self.data)
            # check thumb
            self.set_option('image-thumb-size', '5x5')
            pilthumb = pilopen(
                img.cw_adapt_to('IImage').thumbnail(shadow=False))
            self.assertEqual(pilthumb.size, (5, 5))
            self.assertEqual('PNG', pilthumb.format)
            # check resize 10x5
            self.set_option('image-max-size', '10x5')
            img = cnx.create_entity(
                'File', data=Binary(self.data), data_name=u'20x20.gif')
            self.assertEqual(img.data_format, u'image/gif')
            pilimg = pilopen(img.data)
            self.assertEqual(pilimg.size, (5, 5))
            # also on update
            img.cw_set(data=Binary(self.data))
            img.cw_clear_all_caches()
            pilimg = pilopen(img.data)
            self.assertEqual(pilimg.size, (5, 5))
            # test image smaller than max size
            self.set_option('image-max-size', '40x40')
            img.cw_set(data=Binary(self.data))
            pilimg = pilopen(img.data)
            self.assertEqual(pilimg.size, (20, 20))


class Sha1TC(CubicWebTC):

    def test_init_sha1(self):
        with self.admin_access.client_cnx() as cnx:
            cnx.vreg.config['compute-sha1hex'] = 0
            fobj = cnx.create_entity(
                'File', data_name=u"foo.txt", data=Binary(b"xxx"))
            self.assertEqual(None, fobj.data_sha1hex)

            cnx.vreg.config['compute-sha1hex'] = 1
            fobj = cnx.create_entity(
                'File', data_name=u"foo.txt", data=Binary(b"xxx"))
            self.assertEqual(
                u'b60d121b438a380c343d5ec3c2037564b82ffef3',
                fobj.data_sha1hex)

    def test_modify_data(self):
        with self.admin_access.client_cnx() as cnx:
            cnx.vreg.config['compute-sha1hex'] = 1
            fobj = cnx.create_entity(
                'File', data_name=u"foo.txt", data=Binary(b"xxx"))
            fobj.cw_set(data=Binary(b'yyy'))
            self.assertEqual(
                u'186154712b2d5f6791d85b9a0987b98fa231779c',
                fobj.data_sha1hex)

    def test_manual_set_sha1_forbidden(self):
        with self.admin_access.client_cnx() as cnx:
            cnx.vreg.config['compute-sha1hex'] = 0
            with self.assertRaises(Unauthorized):
                cnx.create_entity(
                    'File', data_name=u"foo.txt", data=Binary(b"xxx"),
                    data_sha1hex=u'0'*40)
                cnx.commit()


if __name__ == '__main__':
    from unittest import main
    main()
