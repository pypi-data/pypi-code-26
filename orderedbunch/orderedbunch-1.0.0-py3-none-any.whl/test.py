import unittest
from collections import OrderedDict as OD
from .bunch import OrderedBunch, \
                   ordered_bunchify, \
                   ordered_unbunchify, \
                   _print_recursive


class TestBunch(unittest.TestCase):
    """ordered_dictify should work with:
            -dictionaries (this will turn them into an OrderedBunch)
            -ordered dictionaries
            -nested dictionaries/ordered dictionaries
            -nested lists of dictionaries/ordered dictionaries
            -nested tuples of dictionaries/ordered dictionaries"""

    def test_ordered_bunchify1(self):
        ddd = OD([('a', 'one'),
                  ('b', 'two'),
                  ('c', OD([('aa', 1),
                            ('bb', 1.23)]))
                  ])
        bbb = ordered_bunchify(ddd)

        a = isinstance(bbb, OrderedBunch)
        b = isinstance(bbb['c'], OrderedBunch)
        c = isinstance(bbb['c']['aa'], int)

        self.assertTrue(a and b and c)

    def test_ordered_bunchify2(self):
        ddd = OD([('a', 'one'),
                  ('b', 'two'),
                  ('c', [('aa', 1),
                         ('bb', 1.23)])
                  ])

        bbb = ordered_bunchify(ddd)

        a = isinstance(bbb, OrderedBunch)
        b = isinstance(bbb['c'], list)
        c = isinstance(bbb['c'][0], tuple)

        self.assertTrue(a and b and c)

    def test_ordered_bunchify3(self):
        ddd = OD()
        ddd['a'] = 'one'
        ddd['b'] = (4, 5, 6)
        ddd['c'] = OD()
        ddd['c']['aa'] = 1
        ddd['c']['bb'] = [1, 2, 3, 4]

        bbb = ordered_bunchify(ddd)

        a = isinstance(bbb, OrderedBunch)
        b = isinstance(bbb['c'], OrderedBunch)
        c = isinstance(bbb['c']['aa'], int)

        self.assertTrue(a and b and c)


    def test_ordered_bunchify4(self):
        ddd = {'a': 'one',
               'b': 'two',
               'c': {
                   'aa': 1,
                   'bb': 1.23
                     }
               }
        ob = ordered_bunchify(ddd)

        a = isinstance(ob,OrderedBunch)
        b = isinstance(ob['c'],OrderedBunch)
        c = isinstance(ob['c']['aa'],int)

        self.assertTrue(a and b and c)

    def test_ordered_bunchify5(self):
        ddd = OD()
        ddd['a'] = 'one'
        ddd['b'] = (4, 5)
        ddd['c'] = OD()
        ddd['c']['aa'] = 1
        ddd['c']['bb'] = [1, 2]

        bbb = ordered_bunchify(ddd)

        a = isinstance(bbb,OrderedBunch)
        b = isinstance(bbb['c'],OrderedBunch)
        c = isinstance(bbb['c']['aa'],int)

        self.assertTrue(a and b and c)

    def test_ordered_bunchify6(self):
        ddd = OD()
        ddd['bb'] = ['mul', 'pan', 'swir']
        ddd['aaa'] = ['mul', 'pan']

        bbb = ordered_bunchify(ddd)

        a = isinstance(bbb, OrderedBunch)
        b = isinstance(bbb['aaa'], list)
        c = isinstance(bbb['aaa'][0], str)

        self.assertTrue(a and b and c)

    def test_ordered_bunchify7(self):
        ddd = OD()
        ddd['b'] = 1
        ddd['a'] = [OD()]
        ddd['a'].append(OD())
        ddd['a'][0]['a'] = ['mul','pan']
        ddd['a'][1]['a'] = ['mmm','ppp']

        bbb = ordered_bunchify(ddd)

        a = isinstance(bbb, OrderedBunch)
        b = isinstance(bbb['b'], int)
        c = isinstance(bbb['a'], list)
        d = isinstance(bbb['a'][0], OrderedBunch)
        e = isinstance(bbb['a'][1], OrderedBunch)
        f = isinstance(bbb['a'][0]['a'], list)
        g = isinstance(bbb['a'][1]['a'], list)

        self.assertTrue(all([a,b,c,d,e,f,g]))

    def test_ordered_bunchify8(self):
        ddd = OD()
        ddd['a'] = 1
        ddd['c'] = [OD()]
        ddd['c'][0]['aa'] = ['mul', 'pan']
        ddd['c'][0]['bb'] = 1.23
        ddd['c'][0]['cc'] = 'mul2'

        bbb = ordered_bunchify(ddd)

        a = isinstance(bbb, OrderedBunch)
        b = isinstance(bbb['a'], int)
        c = isinstance(bbb['c'], list)
        d = isinstance(bbb['c'][0], OrderedBunch)
        e = isinstance(bbb['c'][0]['aa'], list)
        f = isinstance(bbb['c'][0]['bb'], float)
        g = isinstance(bbb['c'][0]['cc'], str)

        # Test the pretty print routine at least completes
        h = isinstance(_print_recursive(bbb), str)

        self.assertTrue(all([a,b,c,d,e,f,g,h]))

    def test_ordered_bunchify9(self):
        ddd = OD()
        ddd['a'] = [[[1, 2], [3, 4]]]

        bbb = ordered_bunchify(ddd)

        a = isinstance(bbb, OrderedBunch)
        b = isinstance(bbb['a'], list)
        c = isinstance(bbb['a'][0], list)
        d = isinstance(bbb['a'][0][1], list)
        e = isinstance(bbb['a'][0][1][0], int)

        # Test the pretty print routine at least completes
        f = isinstance(_print_recursive(bbb), str)

        self.assertTrue(all([a,b,c,d,e,f]))

    def test_print_long_string(self):
        "Add a bunch with a really long string to test wrapping"
        ddd = OD()
        ddd['a'] = [[1,2],[2,3]]
        ddd['longstr'] = 'This is a very long string that should wrap to the ' \
                         'next line when printing.  It is important to make ' \
                         'make sure that all this stuff is correctly formatted.'
        ddd['newod'] = OD()
        ddd['newod']['k1'] = 1.2345

        bbb = ordered_bunchify(ddd)

        a = isinstance(bbb, OrderedBunch)
        b = isinstance(bbb['newod'], OrderedBunch)
        c = isinstance(bbb['newod']['k1'], float)
        d = isinstance(bbb['longstr'], str)


        # Test the pretty print routine at least completes
        e = isinstance(_print_recursive(bbb), str)

        # Test that pretty print return the correct hard coded string
        correctout = "a       : [\n          - [\n            -- 1\n         " \
                     "   -- 2\n          - ]\n          - [\n            " \
                     "-- 2\n            -- 3\n          - ]\n          " \
                     "]\nlongstr : This is a very long string that should " \
                     "wrap to the next line when\n          printing.  It " \
                     "is important to make make sure that all this stuff is\n" \
                     "          correctly formatted.\nnewod   : " \
                     "<class 'orderedbunch.bunch.OrderedBunch'>\n          " \
                     "-k1 : 1.2345"
        f = _print_recursive(bbb) == correctout

        self.assertTrue(all([a,b,c,d,e,f]))

    def test_print_empty_entry(self):
        "Add a bunch with a really long string to test wrapping"
        ddd = OD()
        ddd['a'] = [[1,2],[2,3]]
        ddd['empty'] = None
        ddd['empty2'] = []

        bbb = ordered_bunchify(ddd)

        a = isinstance(bbb, OrderedBunch)
        b = isinstance(bbb['a'], list)
        c = (bbb['empty'] is None)
        d = isinstance(bbb['empty2'], list)


        # Test the pretty print routine at least completes
        e = isinstance(_print_recursive(bbb), str)

        # Test that pretty print return the correct hard coded string
        correctout = 'a      : [\n         - [\n           -- 1\n           ' \
                     '-- 2\n         - ]\n         - [\n           -- 2\n ' \
                     '          -- 3\n         - ]\n         ]\nempty  : ' \
                     'None\nempty2 : [\n         ]'
        f = (_print_recursive(bbb) == correctout)

        self.assertTrue(all([a,b,c,d,e,f]))


if __name__ == '__main__':
    unittest.main()


