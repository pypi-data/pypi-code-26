from unittest import TestCase
from exoticst.dijkstra_shortest_path import DijkstraSearch, make_undirected_weighted_graph


class TestDijkstraSearch(TestCase):
    def test_shortest_paths(self):
        """
                        Graph:
                        1 2 24
                        1 4 20
                        3 1 3
                        4 3 12
        """
        expected_dict_of_weights = {1: 0, 2: 24, 3: 3, 4: 15}
        expected_path = [1, 3, 4, 2]
        edges = [[1, 2, 24], [1, 4, 20], [3, 1, 3], [4, 3, 12]]
        s = 1
        g = make_undirected_weighted_graph(edges)
        dijkstra_search = DijkstraSearch(g)
        path, dict_of_weights = dijkstra_search.shortest_paths(s)
        self.assertEqual(expected_dict_of_weights, dict_of_weights)
        self.assertEqual(expected_path, path)

    def test_find_shortest_paths(self):
        """
                Graph:
                1 2 24
                1 4 20
                3 1 3
                4 3 12
        """
        expected = '24 3 15'

        edges = [[1, 2, 24], [1, 4, 20], [3, 1, 3], [4, 3, 12]]
        s = 1
        g = make_undirected_weighted_graph(edges)
        dijkstra_search = DijkstraSearch(g)
        sorted_weights_str = dijkstra_search.str_of_sorted_shortest_paths(s)
        self.assertEqual(expected, sorted_weights_str)
