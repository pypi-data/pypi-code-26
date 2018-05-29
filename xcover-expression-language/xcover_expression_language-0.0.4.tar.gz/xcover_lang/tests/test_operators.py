from unittest import TestCase

from xcover_lang.utils import eval_expr


class ArithmeticTestCase(TestCase):

    def test_additions(self):
        test_set = {
            '1 + 1': 2,
            '1 + 1 + 1': 3,
            '1 + 0 + 1': 2,
            '1.5 + 1': 2.5,
            '-1 + 2': 1
        }
        for expr, expected_result in test_set.items():
            result, _ = eval_expr(expr)
            self.assertEqual(result, expected_result)

    def test_additions_between_strings(self):
        test_set = {
            '"a" + "b"': 'ab',
            '"a" + "b" + "c"': 'abc'
        }
        for expr, expected_result in test_set.items():
            result, _ = eval_expr(expr)
            self.assertEqual(result, expected_result)

    def test_subtract(self):
        test_set = {
            '1 - 1': 0,
            '1 - 2': -1,
            '0 - 2': -2,
            '-1 - 2': -3
        }
        for expr, expected_result in test_set.items():
            result, _ = eval_expr(expr)
            self.assertEqual(result, expected_result)

    def test_multiply(self):
        test_set = {
            '1 * 1': 1,
            '1 * 0': 0,
            '1 * 1.33333': 1.33333,
            '-1 * 2': -2,
            '2 * -1': -2,
        }
        for expr, expected_result in test_set.items():
            result, _ = eval_expr(expr)
            self.assertEqual(result, expected_result)

    def test_div(self):
        test_set = {
            '1 / 1': 1,
            '3 / 2': 1.5,
            '0 / 1': 0,
            '2 / -1': -2,
            '-2 / 2': -1,
        }
        for expr, expected_result in test_set.items():
            result, _ = eval_expr(expr)
            self.assertEqual(result, expected_result)

    def test_parentheses_rules(self):
        test_set = {
            '1 * 2 + 1': 3,
            '3 * (1 + 2) ': 9,
            '(3 * 3) + (1 + 2)': 12,
        }
        for expr, expected_result in test_set.items():
            result, _ = eval_expr(expr)
            self.assertEqual(result, expected_result)

    def test_arithmetic_precedences(self):
        test_set = {
            '1 + 2 * 2': 5,
            '3 * (1 + 2)': 9,
            '3 * (1 + 2) * 2 + 2 * 2': 22,
        }
        for expr, expected_result in test_set.items():
            result, _ = eval_expr(expr)
            self.assertEqual(result, expected_result)

    def test_negative_numbers(self):
        self.assertEqual(-1, eval_expr('-1')[0])
        self.assertEqual(-0, eval_expr('-0')[0])


class LogicalOperatorTestCase(TestCase):

    def test_or_operator(self):
        self.assertEqual(eval_expr('1 or 2')[0], 1.0)
        self.assertEqual(eval_expr('0 or 0 or 1')[0], 1.0)

    def test_and_operator(self):
        self.assertEqual(eval_expr('1 and 2')[0], True)
        self.assertEqual(eval_expr('1 and 2 and 0')[0], False)


class EqualitiesTestCase(TestCase):

    def test_inline_equalities(self):
        self.assertEqual(eval_expr('1 == 1')[0], True)
        self.assertEqual(eval_expr('-1 == -1')[0], True)

        self.assertEqual(eval_expr('3 >= 3')[0], True)
        self.assertEqual(eval_expr('3 <= 3')[0], True)

    def test_inline_inequalities(self):
        self.assertEqual(eval_expr('3 <> 3')[0], False)
        self.assertEqual(eval_expr('3 <> 2')[0], True)

        self.assertEqual(eval_expr('1 > 0')[0], True)
        self.assertEqual(eval_expr('1 < 0')[0], False)
