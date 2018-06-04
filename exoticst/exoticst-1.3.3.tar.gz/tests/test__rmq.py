from unittest import TestCase
from exoticst.full_bin_tree_for_rmq import build_helper_tree, rmq, update


################### test helper functions ############################################
def prepare_stupid_rmq(a, f=min):
    return [[f(a[i:j]) for i in range(j)] for j in range(1, len(a) + 1)]


def stupid_rmq(c, i, j):
    return c[j][i] if i < j else c[i][j] if j < i else c[i][i]


######################################################################################


class TestRmq(TestCase):

    ##################################################################################
    def test__prepare_stupid_rmq_min(self):
        self.assertEqual([[5], [3, 3], [3, 3, 7], [3, 3, 4, 4], [3, 3, 4, 4, 8]],
                         prepare_stupid_rmq([5, 3, 7, 4, 8]))

    def test__prepare_stupid_rmq_max(self):
        self.assertEqual([[5], [5, 3], [7, 7, 7], [7, 7, 7, 4], [8, 8, 8, 8, 8]],
                         prepare_stupid_rmq([5, 3, 7, 4, 8], f=max))

    def test__stupid_rmq_1(self):
        a = [5, 3, 7, 4, 8]
        c = prepare_stupid_rmq(a)
        for j in range(1, len(a) + 1):
            for i in range(j):
                self.assertEqual(c[j - 1][i], stupid_rmq(c, i, j - 1))

    ##################################################################################

    def test__build_helper_tree_min_and_max_1(self):
        self.assertEqual([5], build_helper_tree([5]))
        self.assertEqual([5], build_helper_tree([5], f=max, ignore=-float('inf')))

    def test__build_helper_tree_min_and_max_2(self):
        self.assertEqual([5, 5, 7], build_helper_tree([5, 7]))
        self.assertEqual([7, 5, 7], build_helper_tree([5, 7], f=max, ignore=-float('inf')))

    def test__build_helper_tree_sum_1(self):
        self.assertEqual([12, 5, 7], build_helper_tree([5, 7], f=sum, ignore=0))

    def test__build_helper_tree_sum_2(self):
        self.assertEqual([22, 12, 10, 5, 7, 0, 0], build_helper_tree([5, 7, 10], f=sum, ignore=0))

    def test_range_min_query_1(self):
        a = [5]
        t = build_helper_tree([5])
        m = rmq(len(a), t, 0, 0)
        assert 5 == m

    def test_range_max_query_1(self):
        a = [5]
        t = build_helper_tree([5], f=max, ignore=-float('inf'))
        m = rmq(len(a), t, 0, 0, f=max, ignore=-float('inf'))
        assert 5 == m

    ##################################################################################
    def test_range_min_query(self):
        a = [5, 3, 7, 4, 8]
        c = prepare_stupid_rmq(a)
        t = build_helper_tree(a)
        for j in range(1, len(a) + 1):
            for i in range(j):
                self.assertEqual(stupid_rmq(c, i, j - 1), rmq(len(a), t, i, j - 1))

    def test_range_max_query(self):
        a = [5, 3, 7, 4, 8]
        c = prepare_stupid_rmq(a, f=max)
        t = build_helper_tree(a, f=max, ignore=-float('inf'))
        for j in range(1, len(a) + 1):
            for i in range(j):
                self.assertEqual(stupid_rmq(c, i, j - 1), rmq(len(a), t, i, j - 1, f=max, ignore=-float('inf')))

    ##################################################################################
    def test_range_sum_query(self):
        a = [5, 3, 7, 4, 8]
        c = [[sum(a[i:j]) for i in range(j)] for j in range(1, len(a) + 1)]
        t = build_helper_tree(a, f=sum, ignore=0)
        for j in range(1, len(a) + 1):
            for i in range(j):
                self.assertEqual(c[j - 1][i], rmq(len(a), t, i, j - 1, f=sum, ignore=0))

    ##################################################################################

    def test_range_indexes_min_query(self):
        a = [5, 3, 7, 4, 8]
        b = list(enumerate(a))

        def f(lst):
            i, mn = lst[0]
            for j, x in lst:
                if x < mn:
                    i, mn = j, x
            return i, mn

        ign = (0, float('inf'))
        t = build_helper_tree(b, f=f, ignore=ign)
        self.assertEqual([(1, 3), (1, 3), (3, 4), (1, 3), (2, 7), (3, 4), (4, 8), (0, 5), (1, 3), (0, float('inf')),
                          (0, float('inf')), (0, float('inf')), (0, float('inf')), (0, float('inf')),
                          (0, float('inf'))],
                         build_helper_tree(b, f=f, ignore=ign))

        self.assertEqual([(0, 5), (1, 3), (1, 3), (1, 3), (1, 3), (2, 7), (1, 3), (1, 3), (3, 4), (3, 4),
                          (1, 3), (1, 3), (3, 4), (3, 4), (4, 8)],
                         [rmq(len(a), t, i, j - 1, f=f, ignore=ign) for j in range(1, len(a) + 1) for i in range(j)])

    def test_range_indexes_max_query(self):
        a = [5, 3, 7, 4, 8]
        b = list(enumerate(a))

        def f(lst):
            i, mx = lst[0]
            for j, x in lst:
                if x > mx:
                    i, mx = j, x
            return i, mx

        ign = (0, -float('inf'))
        t = build_helper_tree(b, f=f, ignore=ign)

        self.assertEqual([(4, 8), (2, 7), (4, 8), (0, 5), (2, 7),
                          (3, 4), (4, 8), (0, 5), (1, 3),
                          (0, -float('inf')), (0, -float('inf')),
                          (0, -float('inf')), (0, -float('inf')),
                          (0, -float('inf')), (0, -float('inf'))],
                         build_helper_tree(b, f=f, ignore=ign))

        self.assertEqual([(0, 5), (0, 5), (1, 3), (2, 7), (2, 7),
                          (2, 7), (2, 7), (2, 7), (2, 7), (3, 4),
                          (4, 8), (4, 8), (4, 8), (4, 8), (4, 8)],
                         [rmq(len(a), t, i, j - 1, f=f, ignore=ign)
                          for j in range(1, len(a) + 1) for i in range(j)])

    ##################################################################################
    def test_update0_min_max_sum(self):
        self.assertEqual([4], update(1, [4], idx_change=0, change=4))
        self.assertEqual([6], update(1, [5], idx_change=0, change=6, f=max, ignore=-float('inf')))
        self.assertEqual([8], update(1, [5], idx_change=0, change=3, f=sum, ignore=0))
        self.assertEqual([2], update(1, [5], idx_change=0, change=-3, f=sum, ignore=0))

    ##################################################################################
    def test_update_max(self):
        a = [5, 3, 7, 4, 8]
        len_a = len(a)
        t = build_helper_tree(a)
        for j in range(len_a):
            a[j] += 2
            t2 = build_helper_tree(a)
            t3 = update(len_a, t2, idx_change=j, change=a[j], f=max, ignore=-float('inf'))
            assert t2 == t3
            a[j] -= 4
            t2 = build_helper_tree(a)
            t3 = update(len_a, t2, idx_change=j, change=a[j], f=max, ignore=-float('inf'))
            assert t2 == t3

    def test_update_min(self):
        a = [5, 3, 7, 4, 8]
        len_a = len(a)
        t = build_helper_tree(a)
        for j in range(len_a):
            a[j] += 2
            t2 = build_helper_tree(a)
            t3 = update(len_a, t2, idx_change=j, change=a[j])
            self.assertEqual(t2, t3)
            a[j] -= 4
            t2 = build_helper_tree(a)
            t3 = update(len_a, t2, idx_change=j, change=a[j])
            self.assertEqual(t2, t3)

    ##################################################################################
    def test_update_sum(self):
        a = [5, 3, 7, 4, 8]
        len_a = len(a)
        t = build_helper_tree(a)
        for j in range(len_a):
            a[j] += 2
            t2 = build_helper_tree(a)
            t3 = update(len_a, t2, idx_change=j, change=2, f=sum, ignore=0)
            self.assertEqual(t2, t3)
            a[j] -= 4
            t2 = build_helper_tree(a)
            t3 = update(len_a, t2, idx_change=j, change=-4, f=sum, ignore=0)
            self.assertEqual(t2, t3)

    ##################################################################################
