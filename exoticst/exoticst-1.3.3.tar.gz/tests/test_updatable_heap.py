from unittest import TestCase
from exoticst.heap_with_update import UpdatableHeap


class TestUpdatableHeap(TestCase):
    def test_empty_heap_sort_case(self):
        l2 = []
        expected = []
        heapq = UpdatableHeap()
        realised = heapq.heapsort(l2)
        self.assertEqual(expected, realised)

    def test_sorted_iterator(self):
        l2 = [
            (5, 5, 5), (1, 1, 1), (3, 3, 3), (0, 0, 0), (10, 10, 10), (11, 11, 11), (9, 9, 9), (8, 8, 8), (7, 7, 7),
            (2, 2, 2), (6, 6, 6)
        ]
        expected = [
            (0, 0, 0), (1, 1, 1), (2, 2, 2), (3, 3, 3), (5, 5, 5),
            (6, 6, 6), (7, 7, 7), (8, 8, 8), (9, 9, 9), (10, 10, 10), (11, 11, 11)
        ]
        heapq = UpdatableHeap()
        for el in l2:
            heapq.push(*el)
        realised = list(heapq.sorted_iterator())
        self.assertEqual(expected, realised)

    def test_empty_heap_sort_list(self):
        l2 = [
            (5, 5, 5), (1, 1, 1), (3, 3, 3), (0, 0, 0), (10, 10, 10), (11, 11, 11), (9, 9, 9), (8, 8, 8), (7, 7, 7),
            (2, 2, 2), (6, 6, 6)
        ]
        expected = [
            (0, 0, 0), (1, 1, 1), (2, 2, 2), (3, 3, 3), (5, 5, 5),
            (6, 6, 6), (7, 7, 7), (8, 8, 8), (9, 9, 9), (10, 10, 10), (11, 11, 11)
        ]
        heapq = UpdatableHeap()
        realised = heapq.heapsort(l2)
        self.assertEqual(expected, realised)

    def test_generic_heap_sort_case(self):
        l2 = [
            (3, 3, 3), (0, 0, 0), (10, 10, 10), (11, 11, 11), (9, 9, 9), (8, 8, 8), (7, 7, 7),
            (2, 2, 2), (6, 6, 6)
        ]
        expected = [
            (0, 0, 0), (1, 1, 1), (2, 2, 2), (3, 3, 3), (5, 5, 5),
            (6, 6, 6), (7, 7, 7), (8, 8, 8), (9, 9, 9), (10, 10, 10), (11, 11, 11)
        ]
        heapq = UpdatableHeap()
        for x in ((5, 5, 5), (1, 1, 1), ):
            heapq.push(*x)
        realised = heapq.heapsort(l2)
        self.assertEqual(expected, realised)

    def test_generic_heap_update_case(self):
        l2 = [
            (5, 5, 5), (1, 1, 1), (3, 3, 3), (0, 0, 0), (10, 10, 10), (11, 11, 11), (9, 9, 9), (8, 8, 8), (7, 7, 7),
            (2, 2, 2), (6, 6, 6)
        ]
        expected = [
            (0, 0, 0), (1, 1, 1), (2, 2, 2), (5, 5, 5), (6, 6, 6), (7, 7, 7),
            (8, 8, 8), (9, 9, 9), (10, 10, 10), (11, 11, 11), (20, 3, 3),
        ]
        heapq = UpdatableHeap()
        for x in l2:
            heapq.push(*x)
        heapq.update(*(20, 3, 3))
        realised = [(x.heap_key, x.key, x.data) for x in heapq.sorted_iterator()]
        self.assertEqual(expected, realised)
