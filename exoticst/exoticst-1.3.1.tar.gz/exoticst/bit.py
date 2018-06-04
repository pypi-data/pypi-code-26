"""
Binary Indexed Tree AKA Fenwick Tree

The structure is convenient to use when there is a need to use prefix sums for an array,
elements of which are updated often.
While the brute force approach in the worse case requires to recalculate all the prefix sums on change of an element,
which takes O(n) time, while the change of the element itself takes O(1) time, O(n) space.
BIT structure takes O(log(n)) time to calculate a prefix sum, and O(log(n)) to update the structure on element change,
the same space complexity.

Initiation of the structure requires O(n*log(n)) time. This means that in case when the underlying array elements
are not going to be changed, or the number of such changes much smaller than log(n), brute force method would be faster.

References:
https://www.youtube.com/watch?v=v_wj_mOAlig&t=1s
https://cs.stackexchange.com/questions/10538/bit-what-is-the-intuition-behind-a-binary-indexed-tree-and-how-was-it-thought-a

Also see full_bin_tree_for_rmq module in this library.  It uses a very similar structure with slightly different
implementation of the construction and the search.   In addition to the range sum, the range max/min queries are
implemented there as well, with the usage described in the documentation.
"""


class BITError(Exception):
    pass


class Bit(object):
    """
    Implementation of Binary Index Tree AKA Fenwick Tree.
    Internally, using indexes in the range(1,n+1) to enable specific BIT indexing trick, which is based on
    on the formula for the calculation of  the last set bit in a binary number:  x&(-x)
    e.g., the last set bit for x = 0110 is 0010, and the value of the expression x & (-x) is:
            x & (-1) = 0110 & (-0110) = 0110 & (1001 + 0001) = 0110 & 1010 = 0010
    The structure maintains sums of log(n) ranges of the underlying array and a prefix sum can be calculated from
    a subset of these range sums, therefore, in o(log(n)) time.  Updating the structure on a change of an element
    of an array requires to update O(log(n)) range sums, i.e., takes O(log(n)) time.
    """

    def __init__(self, n):
        """
        Moved initialisation into init_with_list() method for convenience.
        Don't forget to always use init_with_list() method first.
        """
        if n < 1:
            raise BITError('Illegal input length')
        self.tree_lst = [0] * (n + 1)

    def init_with_list(self, lst):
        """

        This implementation requires O(n*lg(n))  operations.
        :param lst: the list to initialize the tree with
        :return:
        """
        n = len(lst)
        if n < 1:
            raise BITError('Illegal input length')
        self.tree_lst = [0] * (n + 1)
        for j, x in enumerate(lst):
            self.add_at(j, x)

    def add_at(self, idx, increment):
        """
        Increment element at original index idx and update the BIT structure,
         O(lg(n))  operations required
        :param idx:         original index of the element to increment (BIT index = idx+1
        :param increment:   the value to increment
        :return:            updates the tree in place, returns None
        """
        bit_idx = idx + 1
        while bit_idx < len(self.tree_lst):
            self.tree_lst[bit_idx] += increment
            bit_idx += (bit_idx & -bit_idx)

    def prefix_sum(self, idx):
        """
        O(lg(n))  operations required
        :param j:   original index to calculate cumulative sum from 1 up to and including j
        :return:    the cumulative sum of the elements with indexes from 1 up to and including j,
                    AKA prefix sum
        """
        bit_idx = idx + 1
        pr_sum = 0
        while bit_idx:
            pr_sum += self.tree_lst[bit_idx]
            bit_idx -= (bit_idx & -bit_idx)
        return pr_sum

    def range_sum(self, i, j):
        """
        Cumulative sum of the elements between and including to the indexes i and j
        :param i:   the beginning index of the segment of elements to sum up
        :param j:   the last index of the segment of the elements to sum up
        :return:    the sum of the elements between and including to indices i and j
        """
        return self.prefix_sum(j) - self.prefix_sum(i - 1)

    def element(self, j):
        """
        Find and return the value of the element at BIT index j
        :param j:   element's index in the original list
        :return:    element(j)
        """
        return self.prefix_sum(j) - self.prefix_sum(j - 1)


if __name__ == "__main__":
    """
    Keeping some tests here as examples of the usage.
    Unit tests are also presented in the tests package.
    """


    def test_element():
        lst = [1, 5, 10, 100]
        bit = Bit(len(lst) + 1)
        bit.init_with_list(lst)
        elements = [bit.element(j) for j in range(len(lst))]
        # print(elements)
        assert lst == elements
        print('test_element passed')


    def test_range_sum():
        lst = [1, 5, 10, 100]
        bit = Bit(len(lst) + 1)
        bit.init_with_list(lst)
        expected_0_2 = 16
        realised = bit.range_sum(0, 2)
        # print(realised)
        assert expected_0_2 == realised
        print('test_range_sum passed')


    test_element()
    test_range_sum()
