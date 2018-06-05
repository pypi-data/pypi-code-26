from unittest import TestCase

from xcover_lang.utils import eval_expr


class DictionaryTestCase(TestCase):

    def setUp(self):
        self.expr = '''
        foo = {
            "UK": 1,
            "CN": 2,
            "AU": 3
        }
        '''

    def test_dictionary(self):
        r, context = eval_expr(self.expr)

        self.assertDictEqual(context['foo'], {
            "UK": 1,
            "CN": 2,
            "AU": 3
        })

    def test_dictionary_lookup(self):
        expr = self.expr + '''
        au = foo["AU"]
        uk = foo["UK"]
        ru = foo["RU"]
        jp = foo["JP"] or 0
        '''
        r, context = eval_expr(expr)
        self.assertEqual(context['uk'], 1.0)
        self.assertEqual(context['au'], 3.0)
        self.assertEqual(context['jp'], 0.0)
        self.assertIsNone(context['ru'])
