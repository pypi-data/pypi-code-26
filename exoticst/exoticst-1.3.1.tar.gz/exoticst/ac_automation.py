"""
This implementation of slightly modified Aho-Corasick algorithm takes a list of pattern strings and a list of scores
for each pattern and efficiently builds a slightly modified Aho-Corasick structure that for a given string,
calculates the cumulative scores of each pattern substring in the string, i.e, the number of the occurrences of
of each pattern multiplied by the given scores of the pattern.  The pattern can be repeated with the different scores
in the pattern/scores lists.  All the occurrences of a pattern would be accounted for.
E.g., the pattern "aa" would be counted twice in "aaa".

Please see the tests for the detailed examples of the calculation requirements and the outputs.

A good lecture on the Aho-Corasick Algorithm is, for example, here:
https://web.stanford.edu/class/cs166/lectures/02/Small02.pdf
"""

from collections import Counter, defaultdict


class Automaton(object):
    """
    An implementation of a slightly modified Aho-Corasick algorithm.
    This implementation takes a list of pattern strings and a list of scores for each pattern and efficiently builds
    a slightly modified Aho-Corasick structure that for a given string, calculates the cumulative scores of
    each pattern substring in the string, i.e, the number of the occurrences of each pattern multiplied by the
    given scores of the pattern.  The pattern can be repeated with the different scores in the pattern/scores lists.
    All the occurrences of a pattern would be accounted for.  E.g., the pattern "aa" would be counted twice in "aaa".
    Please see the tests for the detailed examples of the calculation requirements and the outputs.

    """

    class Node(object):
        def __init__(self, label):
            self.label = label
            self.d_children = {}
            self.output = defaultdict(list)
            self.fail = None

        def add_word(self, word, idx, h):
            self.output[word].append((idx, h))

        def children(self):
            return self.d_children.items()

        def get_child(self, char):
            return self.d_children.get(char)

        def add_child_if_absent(self, char):
            return self.d_children.setdefault(char, Automaton.Node(char))

    def __init__(self):
        self.root = Automaton.Node('1')

    def _add_word(self, word, idx, h):
        n = self.root
        for j, c in enumerate(word):
            n = n.add_child_if_absent(c)
        n.add_word(word, idx, h)

    def _build_fail(self):
        self.root.fail = self.root
        q = []
        for k, v in self.root.children():
            v.fail = self.root
            q.append(v)

        while q:
            nxt = []
            for n in q:
                for k, v in n.children():
                    nxt.append(v)
                    n_fail = n.fail
                    n_fail_ch = n_fail.get_child(k)
                    while not n_fail_ch:  # and n_fail != self.root:
                        n_fail = n_fail.fail
                        n_fail_ch = n_fail.get_child(k)
                        if not n_fail_ch and n_fail == self.root:
                            break
                    if n_fail_ch:
                        v.fail = n_fail_ch
                    else:
                        v.fail = self.root
                    for key in v.fail.output.keys():
                        v.output[key].extend(v.fail.output[key])
                q = nxt

    def build(self, words, h_score):
        """

        :param  words:   list of text patterns
        :param  h_score: list of numbers - the scores for the patterns
        :return:  build an amended Aho-Corasick structure, return None
        """
        for i, (w, h) in enumerate(zip(words, h_score)):
            self._add_word(w, i, h)
        self._build_fail()

    def traverse(self, word, first, last):
        """

        :param word:    the text string where to look for the
        :param first:   the fist index in the lists of the patterns and scores
        :param last:    the last index in the lists of the patterns and scores
        :return:        a Counter (dict) with cumulative scores of each patterns
                        of the sublist of patterns between first and last indexes included
                        calculated based on the sublist of the scores between first and last indexes included
                        A pattern string assigned multiple scores would be assigned the sum of the scores.
                        Please see the tests to illustrate the output.
        """
        res = Counter()
        n = self.root
        for i, c in enumerate(word):
            n_ch = n.get_child(c)
            while not n_ch:
                n = n.fail
                n_ch = n.get_child(c)
                if not n_ch and n == self.root:
                    break
            if n_ch:
                n = n_ch
                for word2 in n.output.keys():
                    for (idx, h) in n.output[word2]:
                        if first <= idx <= last:
                            res[word2] += h
        return res


if __name__ == '__main__':
    """
    Keeping some tests here as examples of the usage.
    Unit tests are also presented in the tests package.
    """


    def test0():
        words = ['he', 'she', 'his', 'her', 'hers']
        h_score = [1, 3, 2, 4, 5]
        ac = Automaton()
        ac.build(words, h_score)
        expected = Counter({'hers': 10, 'she': 9, 'her': 8, 'he': 3, 'his': 2})
        res = ac.traverse('shershehishers', 0, len('shershehishers') - 1)
        assert expected == res
        print('test0 passed')


    def test1():
        words = ['he', 'she', 'his', 'her', 'hers']
        h_score = [1, 3, 2, 4, 5]
        ac = Automaton()
        ac.build(words, h_score)  # we do not want to have substring repeated in the words
        expected = Counter()
        res = ac.traverse('xyz', 0, 2)
        assert expected == res
        print('test1 passed')


    def test2():
        words = ['he', 'she', 'his', 'her', 'hers']
        h_score = [1, 3, 2, 4, 5]
        ac = Automaton()
        ac.build(words, h_score)
        expected = Counter({'she': 9, 'his': 2})
        res = ac.traverse('shershehishers', 1, 2)
        assert expected == res
        print('test2 passed')


    def test3():
        words = ['a', 'b', 'c', 'aa', 'd', 'b']
        h_score = [1, 2, 3, 4, 5, 6]
        ac = Automaton()
        ac.build(words, h_score)
        expected = Counter({'c': 3, 'b': 8, 'aa': 8, })
        res = ac.traverse('caaab', 1, 5)
        assert expected == res
        print('test3 passed')


    test0()
    test1()
    test2()
    test3()
