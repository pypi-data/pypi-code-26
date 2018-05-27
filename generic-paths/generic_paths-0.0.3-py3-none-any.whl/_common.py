""" Internal utilities. """


def reverse_path(start, end, prev):
    """ Returns the path from start to end, given a previous table. """
    path = []
    while end != start:
        path.append(end)
        end = prev[end]
    path.append(start)
    path.reverse()
    return path
