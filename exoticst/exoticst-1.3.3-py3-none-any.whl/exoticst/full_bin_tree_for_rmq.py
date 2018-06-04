"""
Performing Range Minimum Queries, Range Maximum Queries, Range Sum Queries in O(log(n)) using a prebuilt structure.
Building a full binary tree and using it for Range Minimum Queries, Range Maximum Queries, Range Sum Queries
(A full binary tree is a tree in which every node has either 0 or 2 children.)
The construction takes O(n) time with O(n) an additional space for the array with the tree;
The update of the range query tree in O(log(n)) time with O(1) additional space (works for max/min as well as for sum)

Here the Range Queries take O(log(n)) time, which is not optimal but often good enough, while the
known (at least to me) structure that gives O(1) time is much more complicated than this one.

The full bin tree we are constructing here is kept in an array (a Python list) in a similar way to the heap structure.
The 0th element corresponds to the root, the indexes of the two children of a node at i are 2*i+1 and 2*i+2, while
the index of the parent of a node at k is (k-1)//2

For the given construction, the root of a subtree will contain a MIN (or Max, or Sum) of the subtree.  A variant of the
construction may contain an index in the original array of the MIN (or Max, or Sum) of the subtree.

Examples of using the code for a given array a and range  [i,j] (i and j included) are here and also presented
as tests in the __main__ function for this module below.

To find the range minimum:
t = build_helper_tree(a)
min_i_j = rmq(len(a), t, q_st=i, q_end=j)

To find the range maximum:
t = build_helper_tree(a, f=max, ignore=-float('inf))
min_i_j = rmq(len(a), t, q_st=i, q_end=j, f=max, ignore=-float('inf))

To find the range sum:
t = build_helper_tree(a, f=sum, ignore=0)
min_i_j = rmq(len(a), t, q_st=i, q_end=j, f=sum, ignore=0)

To update the prebuilt range query tree t for min, where the new value of a at index j is ch:
new_t = update(len(a), t, idx_change=j, change=ch)

To update the prebuilt range query tree t for max, where the new value of a at index j is ch:
new_t = update(len(a), t, idx_change=j, change=ch, f=max, ignore=-float('inf))

To update the prebuilt range query tree t for sum, where the new value of a at index j is new_value:
new_t = update(len(a), t, idx_change=j, change=(new_value-a[j]), f=sum, ignore=0)

It is also possible to prepare and perform the Range Minimum/Maximum Queries in the second definition of the RMQ,
i.e., to search for the indexes of the max/min in the given ranges, with the same times/space characteristics.
For the examples, see test_range_indexes_min_query() and test_range_indexes_max_query() below.

Thus, to find an index of the minimal element in the given range(i, j+1) of the list a, one can do the following:
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
rmq(len(a), t, i, j, f=f, ignore=ign)[0]    # the function returns tuple in the form (index, min_value)

To find the index of the max element in the range, replace the ign and f with the following:
def f(lst):
    i, mx = lst[0]
    for j, x in lst:
        if x > mx:
            i, mx = j, x
    return i, mx
ign = (0, -float('inf'))
and use the same calls:
t = build_helper_tree(b, f=f, ignore=ign)
rmq(len(a), t, i, j, f=f, ignore=ign)[0]    # the function returns tuple in the form (index, max_value)

"""
from math import ceil, log2


def build_helper_tree(a, f=min, ignore=float('inf')):
    """
    :param a: the original array (list) the full binary RMQ tree to be constructed for
    :param f: min or max (or "similar") function
    :param ignore:  e.g., it is float('inf') if f==min else -float('inf') if f==max else 0 #if f==sum
    :return:  the full binary tree to be used for Rage Queriess (RQ) of a
    """

    def _bld(start, end, t, idx=0):
        if start > end:
            t[idx] = ignore
        if start == end:
            t[idx] = a[start]
        else:
            mid = start + (end - start) // 2
            shift = idx * 2
            t[idx] = f([_bld(start, mid, t, idx=(shift + 1)),
                       _bld(mid + 1, end, t, idx=(shift + 2))])
        return t[idx]

    n = len(a)
    d = 2 ** (int(ceil(log2(n))))  # int was needed in older versions of Python
    m = 2 * d - 1  # n leaves => n - 1 internal nodes;  tree height = int(ceil(log2(n))
    fbt = [ignore for j in range(m)]
    _bld(0, n - 1, fbt, idx=0)
    return fbt


def rmq(len_a, t, q_st, q_end, f=min, ignore=float('inf')):
    """

    :param len_a:   the array to search min
    :param t:       the full binary tree for RQs, has to be prepared before calling this function
    :param q_st:    starting position of the query range
    :param q_end:   ending position of the query range
    :param f:       min or max (or "similar") function
    :param ignore:  e.g., it is float('inf') if f==min else -float('inf') if f==max else 0 #if f==sum
    :return:        the value of f of elements of a with the indexes in [q_st, q_end] range including both the ends
    """

    def _rmq(start, end, idx=0):
        if end < q_st or q_end < start:
            return ignore
        if q_st <= start and end <= q_end:
            return t[idx]
        else:
            mid = start + (end - start) // 2
            shift = idx * 2
            return f([_rmq(start, mid, idx=(shift + 1)),
                      _rmq(mid + 1, end, idx=(shift + 2))])

    if q_st < 0 or q_end > len_a - 1 or q_st > q_end:
        raise RuntimeError("Invalid range arguments")
    return _rmq(start=0, end=len_a - 1, idx=0)


def update(len_a, t, idx_change, change, f=min, ignore=float('inf')):
    """
    Given an index in the original array a and the change to be applied at this index, update the
    full binary tree to be used for Range Queries
    :param len_a:   the array to search min
    :param t:       the full binary tree for RMQ, has to be prepared before calling this function
    :param idx_change:  the index in a where the element is being updated
    :param change:      f-specific change to idx_change-th element of a, e.g., a_new[idx_change] for f=sum,
                        or a_new[idx_change] - a[idx_change] for f = min/max
    :param f: min or max (or "similar") function
    :param i  ignore:  e.g., it is float('inf') if f==min else -float('inf') if f==max else 0 #if f==sum
    :return:  the full binary tree updated with the new value at a given index, to be used for RQs of a
    """
    if not (0 <= idx_change <= len_a - 1):
        raise IndexError("idx_change=%d is out of bounds" % idx_change)
    idx = 0
    s, e = 0, len_a - 1
    while s <= e and idx < len(t):
        t[idx] = f((t[idx], change))
        mid = s + (e - s) // 2
        if idx_change <= mid:
            e = mid
            idx = 2 * idx + 1
        else:
            s = mid + 1
            idx = 2 * idx + 2
    return t


if __name__ == '__main__':
    """
    Keeping some tests here as examples of the usage.
    Unit tests are also presented in the tests package.
    """


    ####################################################################################
    def __prepare_stupid_rmq(a, f=min):
        return [[f(a[i:j]) for i in range(j)] for j in range(1, len(a) + 1)]


    def __stupid_rmq(c, i, j):
        return c[j][i] if i < j else c[i][j] if j < i else c[i][i]


    def test__prepare_stupid_rmq_1():
        assert ([[5], [3, 3], [3, 3, 7], [3, 3, 4, 4], [3, 3, 4, 4, 8]] ==
                __prepare_stupid_rmq([5, 3, 7, 4, 8]))
        assert ([[5], [5, 3], [7, 7, 7], [7, 7, 7, 4], [8, 8, 8, 8, 8]] ==
                __prepare_stupid_rmq([5, 3, 7, 4, 8], f=max))


    def test__stupid_rmq_1():
        a = [5, 3, 7, 4, 8]
        c = __prepare_stupid_rmq(a)
        for j in range(1, len(a) + 1):
            for i in range(j):
                assert c[j - 1][i] == __stupid_rmq(c, i, j - 1)


    ####################################################################################

    def test__build_helper_tree_min_and_max_1():
        assert [5] == build_helper_tree([5])
        assert [5] == build_helper_tree([5], f=max, ignore=-float('inf'))


    def test__build_helper_tree_min_and_max_2():
        assert [5, 5, 7] == build_helper_tree([5, 7])
        assert [7, 5, 7] == build_helper_tree([5, 7], f=max, ignore=-float('inf'))


    def test__build_helper_tree_sum_1():
        assert [12, 5, 7] == build_helper_tree([5, 7], f=sum, ignore=0)


    def test__build_helper_tree_sum_2():
        assert [22, 12, 10, 5, 7, 0, 0] == build_helper_tree([5, 7, 10], f=sum, ignore=0)


    def test_range_min_query_1():
        a = [5]
        t = build_helper_tree([5])
        m = rmq(len(a), t, 0, 0)
        assert 5 == m


    def test_range_max_query_1():
        a = [5]
        t = build_helper_tree([5], f=max, ignore=-float('inf'))
        m = rmq(len(a), t, 0, 0, f=max, ignore=-float('inf'))
        assert 5 == m


    def test_range_min_query():
        a = [5, 3, 7, 4, 8]
        c = __prepare_stupid_rmq(a)
        t = build_helper_tree(a)
        for j in range(1, len(a) + 1):
            for i in range(j):
                assert __stupid_rmq(c, i, j - 1) == rmq(len(a), t, i, j - 1)


    def test_range_max_query():
        a = [5, 3, 7, 4, 8]
        c = __prepare_stupid_rmq(a, f=max)
        t = build_helper_tree(a, f=max, ignore=-float('inf'))
        for j in range(1, len(a) + 1):
            for i in range(j):
                assert __stupid_rmq(c, i, j - 1) == rmq(len(a), t, i, j - 1, f=max, ignore=-float('inf'))


    def test_range_sum_query():
        a = [5, 3, 7, 4, 8]
        c = [[sum(a[i:j]) for i in range(j)] for j in range(1, len(a) + 1)]
        t = build_helper_tree(a, f=sum, ignore=0)
        for j in range(1, len(a) + 1):
            for i in range(j):
                assert c[j - 1][i] == rmq(len(a), t, i, j - 1, f=sum, ignore=0)


    def test_range_indexes_min_query():
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
        # print('t = ',t)
        assert [(1, 3), (1, 3), (3, 4), (1, 3), (2, 7),
                (3, 4), (4, 8), (0, 5), (1, 3), (0, float('inf')),
                (0, float('inf')), (0, float('inf')),
                (0, float('inf')), (0, float('inf')), (0, float('inf'))] == build_helper_tree(b, f=f, ignore=ign)
        # print('a = ',a)
        # print([(i, j-1) for j in range(1, len(a)+1) for i in range(j)])
        # print([rmq(len(a), t, i, j - 1, f=f, ignore=ign) for j in range(1, len(a)+1) for i in range(j)])
        assert [(0, 5), (1, 3), (1, 3), (1, 3), (1, 3),
                (2, 7), (1, 3), (1, 3), (3, 4), (3, 4),
                (1, 3), (1, 3), (3, 4), (3, 4), (4, 8)] == [rmq(len(a), t, i, j - 1, f=f, ignore=ign)
                                                            for j in range(1, len(a) + 1) for i in range(j)]


    def test_range_indexes_max_query():
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
        # print('t = ',t)
        assert [(4, 8), (2, 7), (4, 8), (0, 5), (2, 7),
                (3, 4), (4, 8), (0, 5), (1, 3),
                (0, -float('inf')), (0, -float('inf')),
                (0, -float('inf')), (0, -float('inf')),
                (0, -float('inf')), (0, -float('inf'))] == build_helper_tree(b, f=f, ignore=ign)
        # print('a = ',a)
        # print([(i, j-1) for j in range(1, len(a)+1) for i in range(j)])
        # print([rmq(len(a), t, i, j - 1, f=f, ignore=ign) for j in range(1, len(a)+1) for i in range(j)])
        assert [(0, 5), (0, 5), (1, 3), (2, 7), (2, 7),
                (2, 7), (2, 7), (2, 7), (2, 7), (3, 4),
                (4, 8), (4, 8), (4, 8), (4, 8), (4, 8)] == [rmq(len(a), t, i, j - 1, f=f, ignore=ign)
                                                            for j in range(1, len(a) + 1) for i in range(j)]


    def test_update0_min_max_sum():
        assert [4] == update(1, [4], idx_change=0, change=4)
        assert [6] == update(1, [5], idx_change=0, change=6, f=max, ignore=-float('inf'))
        assert [8] == update(1, [5], idx_change=0, change=3, f=sum, ignore=0)
        assert [2] == update(1, [5], idx_change=0, change=-3, f=sum, ignore=0)


    def test_update_max():
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


    def test_update_min():
        a = [5, 3, 7, 4, 8]
        len_a = len(a)
        t = build_helper_tree(a)
        for j in range(len_a):
            a[j] += 2
            t2 = build_helper_tree(a)
            t3 = update(len_a, t2, idx_change=j, change=a[j])
            assert t2 == t3
            a[j] -= 4
            t2 = build_helper_tree(a)
            t3 = update(len_a, t2, idx_change=j, change=a[j])
            assert t2 == t3


    def test_update_sum():
        a = [5, 3, 7, 4, 8]
        len_a = len(a)
        t = build_helper_tree(a)
        for j in range(len_a):
            a[j] += 2
            t2 = build_helper_tree(a)
            t3 = update(len_a, t2, idx_change=j, change=2, f=sum, ignore=0)
            assert t2 == t3
            a[j] -= 4
            t2 = build_helper_tree(a)
            t3 = update(len_a, t2, idx_change=j, change=-4, f=sum, ignore=0)
            assert t2 == t3

    test__build_helper_tree_min_and_max_1()
    test__build_helper_tree_min_and_max_2()
    test__build_helper_tree_sum_1()
    test__build_helper_tree_sum_2()
    test_range_min_query_1()
    test_range_max_query_1()
    test__prepare_stupid_rmq_1()
    test__stupid_rmq_1()
    test_range_min_query()
    test_range_max_query()
    test_range_sum_query()
    test_update0_min_max_sum()
    test_update_min()
    test_update_max()
    test_update_sum()
    test_range_indexes_min_query()
    test_range_indexes_max_query()
