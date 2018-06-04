"""
**Assume** there are no negative weights in the graph. It can be either directed or undirected.

This is a relatively fast implementation of classical Dijkstra short path algorithm:
it uses the UpdatableHeap implementation of the heap, which updates (decreases) values
of an internal element in logarithmic time, instead of sorting the whole heap each time
(e.g., as the implementation from the standard Python library heapq does)
The time complexity is O((E + V)log(V) where E and V are the numbers of edges and vertices respectively.
"""

from exoticst.heap_with_update import HeapElement, UpdatableHeap
from collections import defaultdict


class WeightedGraph(object):
    """
    For example, see make_undirected_weighted_graph() function below
    """

    def __init__(self, lst_of_vertices, adj_list):
        self.v = lst_of_vertices
        self.adj_list = adj_list


######################################################################################
class DijkstraSearch(object):
    """
    This implementation of Dijkstra shortest path algorithm used UpdatableHeap, which is
    asymptotically more efficient than the heapq implementation from the standard Python library
    """

    def __init__(self, g):
        """
        :param g: WeightedGraph object, where its adj_list *assume* to be a dict, with the vertices as keys and
                  the dictionaries {vertex, weight) as items, i.e., graph.adj_list[vertex1][vertex2] is
                  a weight of the edge between vertex1 and vertex2
        """
        self.g = g
        self.queue = UpdatableHeap()
        self.prev = set()
        self.vds = {}

    def init_q(self, s):
        """
        The method is *not used*, it is optimized away in the find_shortest_paths().
        It is *left here only to illustrate* the classical description of the preparation step in Dijkstra algorithm.
        :param s: The source vertex
        """
        for v in self.g.v:
            if v != s:
                vd = HeapElement(heap_key=float('inf'), key=v, data=None)
                self.queue.push(*vd)
            else:
                vd = HeapElement(heap_key=0, key=s, data=None)
                self.queue.push(*vd)
            self.vds[vd.key] = vd

    def shortest_paths(self, s):
        """
        Calculate the shortest distances from the source vertex to the other vertices reachable from s
        :param s:   the source node
        :return:    a dictionary with vertices as the keys and the correspondent distances from the source s as values
                    the dictionary also contains s as a key with 0 as the shortest distance from s to s
        """
        path = []
        vd = HeapElement(heap_key=0, key=s, data=None)
        self.queue.push(*vd)
        self.vds[vd.key] = vd
        while len(self.queue):
            current = self.queue.pop()  # the next element on the shortest path from the source
            if current.key not in self.prev:
                path.append(current.key)
                self.prev.add(current.key)
            for (u, weight) in self.g.adj_list[current.key].items():
                if u not in self.prev:
                    if ((not self.vds.get(u)) or
                            (self.vds.get(u) and (current.heap_key + weight < self.vds[u].heap_key))):
                        new_heap_key = current.heap_key + weight
                        self.vds[u] = HeapElement(heap_key=new_heap_key, key=u, data=None)
                        self.queue.decrease(*self.vds[u])  # here we know that new weight is less than previous one
        return path, {vertex: heap_el.heap_key for (vertex, heap_el) in self.vds.items()}

    def find_shortest_paths(self, s):
        """
        Calculate a list of N-1 space separated integers denoting the shortest distance of N-1 vertices other than S
        from starting position S in increasing order of their labels. For unreachable vertices, use -1.

        :param s:  the source node
        :return:   a list of N-1 integers denoting the shortest distance of N-1 vertices other than S from
                   starting position S in increasing order of their labels. For unreachable vertices, use -1.
        """
        self.shortest_paths(s)

        sorted_vertices = sorted(self.vds.keys())
        sorted_weights = [self.vds[v].heap_key if v in sorted_vertices else '-1' for v in self.g.v if v != s]
        return sorted_weights

    def str_of_sorted_shortest_paths(self, s):
        """
        Output a string consisting N-1 space-separated integers denoting the shortest distance of N-1 vertices
        other than S from starting position S in increasing order of their labels. For unreachable vertices use -1.
        :param s:  the source node
        :return:   a string consisting N-1 space-separated integers denoting the shortest distance of N-1 vertices other
                   than S from starting position S in increasing order of their labels. For unreachable vertices use -1.
        """
        sws = self.find_shortest_paths(s)
        return ' '.join([str(w) if w != float('inf') else '-1' for w in sws])


######################################################################################

def make_undirected_weighted_graph(edges):
    """
    A convenience function, which if needed, converts a graph to undirected graph,
    also if there are two edge with different weights, only the one with the smaller weights
    would be left in the output.  This wouldn't change the dijkstra result

    :param edges: an iterable containing triples vertex1,vertex2,weight;
    :return: adjacency list of the resulting WeightedGraph object,
             where its adj_list being a dict, with the vertices as keys and
             the dictionaries {vertex, weight) as items, i.e.,
             graph.adj_list[vertex1][vertex2] is a weight of the edge between vertex1 and vertex2
    """
    adj_list = defaultdict(dict)
    for edge in edges:
        x, y, r = edge
        if (x not in adj_list) or (y not in adj_list[x]):
            adj_list[x][y] = r
        else:
            w = min(adj_list[x][y], r)
            adj_list[x][y] = w
        if (y not in adj_list) or (x not in adj_list[y]):
            adj_list[y][x] = r
        else:
            w = min(adj_list[y][x], r)
            adj_list[y][x] = w

    lst_of_vertices = sorted(adj_list.keys())
    return WeightedGraph(lst_of_vertices, adj_list)
