""" BFS algorithm implementation. """

from collections import deque

from ._common import reverse_path


def bfs(start, neighbours, success):
    """ Find the shortest path using the BFS algorithm.

    The solution is optimal if the graph is unweighted, or if all weights are
    the same. The returned path includes both the start and end nodes. If no
    path exists, None is returned.

    start: Initial node.

    neighbours: Function that returns the neighbours for a given node.

    success: Function that returns True if the goal is achieved, False
    otherwise.
    """
    prev = {start: None}
    queue = deque()
    queue.append(start)

    while queue:
        elem = queue.popleft()
        if success(elem):
            return reverse_path(start, elem, prev)

        for x in neighbours(elem):
            if x not in prev:
                queue.append(x)
                prev[x] = elem

    return None
