from unittest import TestCase
from exoticst.ac_automation import Automaton
from collections import Counter


class TestAutomaton(TestCase):
    def test_traverse_0(self):
        words = ['he', 'she', 'his', 'her', 'hers']
        h_score = [1, 3, 2, 4, 5]
        ac = Automaton()
        ac.build(words, h_score)
        expected = Counter({'hers': 10, 'she': 9, 'her': 8, 'he': 3, 'his': 2})
        res = ac.traverse('shershehishers', 0, len('shershehishers') - 1)
        self.assertEqual(expected, res)

    def test_traverse_1(self):
        words = ['he', 'she', 'his', 'her', 'hers']
        h_score = [1, 3, 2, 4, 5]
        ac = Automaton()
        ac.build(words, h_score)  # we do not want to have substring repeated in the words
        expected = Counter()
        res = ac.traverse('xyz', 0, 2)
        self.assertEqual(expected, res)

    def test_traverse_2(self):
        words = ['he', 'she', 'his', 'her', 'hers']
        h_score = [1, 3, 2, 4, 5]
        ac = Automaton()
        ac.build(words, h_score)
        expected = Counter({'she': 9, 'his': 2})
        res = ac.traverse('shershehishers', 1, 2)
        self.assertEqual(expected, res)

    def test_traverse_3(self):
        words = ['a', 'b', 'c', 'aa', 'd', 'b']
        h_score = [1, 2, 3, 4, 5, 6]
        ac = Automaton()
        ac.build(words, h_score)
        expected = Counter({'c': 3, 'b': 8, 'aa': 8, })
        res = ac.traverse('caaab', 1, 5)
        self.assertEqual(expected, res)
