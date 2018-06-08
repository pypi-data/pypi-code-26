from __future__ import unicode_literals
from builtins import int

import ctypes
import numpy as np
import unittest

import tecplot as tp
from tecplot import tecutil
from tecplot.constant import PlotType
from tecplot.exception import TecplotLogicError, TecplotTypeError


class TestArgList(unittest.TestCase):
    def test___init__(self):
        arglist = tecutil.ArgList()
        arglist = tecutil.ArgList(aa='aa', bb='bb')
        arglist = tecutil.ArgList(dict(aa='aa', bb='bb'))
        self.assertIsInstance(arglist, tecutil.ArgList)

    def test_len(self):
        with tecutil.ArgList(aa='bb') as arglist:
            self.assertEqual(len(arglist), 1)
        with tecutil.ArgList(aa='bb', cc='dd') as arglist:
            self.assertEqual(len(arglist), 2)
            arglist['ee'] = 3.1415
            self.assertEqual(len(arglist), 3)

    def test_clear(self):
        with tecutil.ArgList(aa='bb') as arglist:
            self.assertEqual(len(arglist), 1)
            arglist.clear()
            self.assertEqual(len(arglist), 0)

    def test_repr(self):
        with tecutil.ArgList(aa='bb') as arglist:
            if isinstance(arglist, tecutil.RemoteArgList):
                self.assertEqual(repr(arglist), "ArgList(aa='bb')")

    def test_str(self):
        with tecutil.ArgList(aa='bb') as arglist:
            if isinstance(arglist, tecutil.RemoteArgList):
                self.assertEqual(str(arglist), str(dict({'aa': 'bb'})))

    def test_iter(self):
        data = dict(aa='bb', cc='dd', ee='ff')
        with tecutil.ArgList(**data) as arglist:
            for k in arglist:
                self.assertIn(k, data)

    def test_index(self):
        data = dict(aa='bb', cc='dd', ee='ff')
        with tecutil.ArgList(**data) as arglist:
            if isinstance(arglist, tecutil.RemoteArgList):
                self.assertIsInstance(arglist._index('aa'), int)
                self.assertIsInstance(arglist._index('cc'), int)
                self.assertEqual(arglist._index('zz'), None)

    def test_unknown(self):
        class UnknownObject:
            pass
        with tecutil.ArgList() as arglist:
            self.assertRaises(TecplotTypeError, arglist.__setitem__, 'a',
                              UnknownObject())

    def test_arb_param(self):
        with tecutil.ArgList() as arglist:
            arglist['aa'] = ctypes.c_size_t(3)
            ret = arglist['aa']
            if isinstance(ret, ctypes.c_size_t):
                ret = ret.value
            self.assertEqual(ret, 3)

            if isinstance(arglist, tecutil.RemoteArgList):
                arglist['bb'] = ctypes.c_size_t(-1)
                ret = arglist['bb']
                self.assertEqual(ret, ctypes.c_int64(ctypes.c_size_t(-1).value).value)

    def test_arb_param_ptr(self):
        with tecutil.ArgList() as arglist:
            if isinstance(arglist, tecutil.RemoteArgList):
                x = ctypes.c_size_t(3)
                p = ctypes.pointer(x)
                arglist['aa'] = p
                ret = arglist['aa']
                self.assertIsInstance(ret, ctypes.POINTER(ctypes.c_int64))
                self.assertEqual(ret.contents.value, 3)

    def test_double(self):
        with tecutil.ArgList() as arglist:
            arglist['aa'] = 3.14
            self.assertEqual(arglist['aa'], 3.14)

    def test_double_ptr(self):
        d = ctypes.pointer(ctypes.c_double(3.1415))
        with tecutil.ArgList() as arglist:
            arglist['aa'] = d
            self.assertIsInstance(arglist['aa'],
                                  ctypes.POINTER(ctypes.c_double))
            self.assertTrue(np.isclose(arglist['aa'].contents, d.contents))

    def test_enum(self):
        with tecutil.ArgList() as arglist:
            arglist['aa'] = PlotType.Cartesian3D
            self.assertEqual(PlotType(arglist['aa']), PlotType.Cartesian3D)

    def test_int(self):
        with tecutil.ArgList() as arglist:
            arglist['aa'] = 1
            self.assertEqual(arglist['aa'], 1)

    def test_list(self):
        with tecutil.ArgList() as arglist:
            if isinstance(arglist, tecutil.RemoteArgList):
                arglist['aa'] = [PlotType.Cartesian2D, PlotType.Cartesian3D]
                ret = arglist['aa']
                ret = ctypes.cast(ret, ctypes.POINTER(ctypes.c_int))
                self.assertEqual(ret[0], PlotType.Cartesian2D.value)
                self.assertEqual(ret[1], PlotType.Cartesian3D.value)

                with self.assertRaises(TecplotTypeError):
                    arglist['bb'] = ['a', 'b']

    def test_index_set(self):
        with tecutil.IndexSet() as s:
            with tecutil.ArgList() as arglist:
                arglist['aa'] = s
                self.assertEqual(arglist['aa'], s)

    def test_string(self):
        with tecutil.ArgList() as arglist:
            arglist['aa'] = 'bb'
            self.assertEqual(arglist['aa'], 'bb')

    def test_stringlist(self):
        with tecutil.StringList() as s:
            with tecutil.ArgList() as arglist:
                arglist['aa'] = s
                self.assertEqual(arglist['aa'], s)

    def test_next(self):
        data = dict(aa='bb', cc='dd')
        with tecutil.ArgList(**data) as arglist:
            if isinstance(arglist, tecutil.RemoteArgList):
                it = iter(arglist)
                item = next(it)
                self.assertIn(item, data)
                item = it.next()
                self.assertIn(item, data)

    def test_index_set_to_arbparam(self):

        with tecutil.IndexSet(1,2,3) as iset:
            addr = ctypes.c_size_t(iset.value)
            ptr = ctypes.c_void_p(addr.value)
            iset2 = ctypes.cast(ptr, tecutil.IndexSet)

            with tecutil.ArgList() as arglist:
                if isinstance(arglist, tecutil.RemoteArgList):
                    arglist['SET'] = iset
                    arglist['ARB'] = addr

                    arb_addr = ctypes.c_size_t(arglist['ARB'])
                    arb_ptr = ctypes.c_void_p(arb_addr.value)
                    arb_iset = ctypes.cast(arb_ptr, tecutil.IndexSet)

                    self.assertEqual(set(iset), set(arb_iset))

    def test_double_array(self):
        arr = [1.,2.,3.]
        with tecutil.ArgList() as arglist:
            if isinstance(arglist, tecutil.RemoteArgList):
                arglist['aa'] = arr
                ret = arglist['aa']
                cptr = ctypes.cast(ret, ctypes.POINTER(ctypes.c_double))
                carr = [float(cptr[i]) for i in range(3)]
                self.assertTrue(np.allclose(arr,carr))

    def test_ignore_none(self):
        with tecutil.ArgList() as arglist:
            arglist['aa'] = None
            self.assertEqual(len(arglist), 0)
            self.assertNotIn('aa', arglist)
            arglist['bb'] = 1
            self.assertEqual(len(arglist), 1)
            self.assertEqual(arglist['bb'], 1)
            arglist['cc'] = None
            self.assertEqual(len(arglist), 1)
            self.assertEqual(arglist['bb'], 1)

    def test_no_duplicates(self):
        if __debug__:
            with tecutil.ArgList(aa=1) as arglist:
                if isinstance(arglist, tecutil.RemoteArgList):
                    with self.assertRaises(TecplotLogicError):
                        arglist['aa'] = 3
                    self.assertEqual(len(arglist), 1)
                    self.assertEqual(arglist['aa'], 1)

    def test_int_iteratable(self):
        def gen():
            for i in [0,1,2]:
                yield i
        with tecutil.ArgList() as al:
            if isinstance(al, tecutil.RemoteArgList):
                al['aa'] = gen()
                cptr = ctypes.cast(al['aa'], ctypes.POINTER(ctypes.c_int64))
                carr = [int(cptr[i]) for i in range(len(list(gen())))]
                self.assertEqual(carr, list(gen()))

    def test_update(self):
        with tecutil.ArgList() as al:
            al.update((('aa',int(3.14)), ('bb',float(3.14)), ('cc',3.14)))
            self.assertEqual(al['aa'],3)
            self.assertEqual(al['bb'],3.14)
            self.assertEqual(al['cc'],3.14)
            al.update((('dd',float('3.14')),), ee='test')
            self.assertEqual(al['dd'],3.14)
            self.assertEqual(al['ee'],'test')
            l = len(al)
            al.update((('yy',None),('zz',None)))
            self.assertEqual(len(al), l)
            al.update(ff='ff')
            self.assertEqual(len(al), l+1)
            self.assertEqual(al['ff'], 'ff')


if __name__ == '__main__':
    from .. import main
    main()
