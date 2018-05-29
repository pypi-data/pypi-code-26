from unittest import TestCase

from xcover_lang.utils import eval_expr


class VariableTestCase(TestCase):

    def test_assignment(self):
        expr = '''
        a = 1
        b = "string"
        c = {"foo": "bar"}
        d = [1, 2, 3]
        '''
        r, context = eval_expr(expr)

        self.assertEqual(context['a'], 1)
        self.assertEqual(context['b'], 'string')
        self.assertDictEqual(context['c'], {"foo": 'bar'})


class BuiltInFunctionTestCase(TestCase):
    def test_min(self):
        result, _ = eval_expr('min(2, 0)')
        self.assertEqual(result, 0)

    def test_max(self):
        result, _ = eval_expr('max(2, 0)')
        self.assertEqual(result, 2)

    def test_membership_testing(self):
        result, _ = eval_expr('"UK" in ["UK", "US"]')
        self.assertTrue(result)
        result, _ = eval_expr('"UK" in ["US"]')
        self.assertFalse(result)

    def test_if_cond_inline_test(self):
        self.assertEqual(eval_expr(
            '''
            if_cond(1 == 1, "yes", "no")
            '''
        )[0], "yes")

    def test_multiple_if_conditions(self):
        context = eval_expr(
            '''
            variable1 = if_cond(1 == 1, "yes", "no")
            variable2 = if_cond(variable1 == "yes", "yes2", "no2")
            '''
        )[1]
        expected = {'variable2': 'yes2'}
        self.assertTrue(set(expected.items()).issubset(set(context.items())))

    def test_if_cond_code_block_test(self):
        self.assertEqual(eval_expr(
            '''
            a = 1
            b = 2
            result = if_cond(a == b, "yes", "no")
            '''
        )[1]['result'], "no")

        # Test "and" in expression and False assignment
        # Return a number instead of a string
        self.assertEqual(eval_expr(
            '''
            a = 1
            b = False
            result = if_cond(a and b, "yes", 1)
            '''
        )[1]['result'], 1)
