import numpy as np


def point_on_axis(pnt_1, pnt_2):
    '''
    :param pnt_1: first point of an image, with (x, y)
    :param pnt_2: second point of an image, with (x, y)
    :return: the point on x axis and point on y axis, it will be None, if no cross point on that axis
    '''
    if pnt_1 is None or pnt_2 is None:
        return None
    if pnt_1[0] == pnt_2[0]:
        return (pnt_1[0], 0), None
    if pnt_1[1] == pnt_2[1]:
        return None, (0, pnt_1[1])

    y = pnt_2[1] - ((pnt_2[1] - pnt_1[1]) / (pnt_2[0] - pnt_1[0])) * pnt_2[0]
    pnt_x_0 = (0, int(y))
    x = pnt_2[0] - pnt_2[1] * ((pnt_2[0] - pnt_1[0]) / (pnt_2[1] - pnt_1[1]))
    pnt_y_0 = (int(x), 0)

    return pnt_x_0, pnt_y_0


def point_respect_line(point, line):
    """
    :param point: point of (x, y)
    :param line:  line of two points (point1, point2),
    :return: an integer that >0, ==0, <0, if == 0 means point lies on the line
    """
    # Method 1: cross product

    # (pnt1, pnt2) = line
    # v1 = [pnt2[0] - pnt1[0], pnt2[1] - pnt1[1]]
    # v2 = [point[0] - pnt1[0], point[1] - pnt1[1]]
    # r = np.cross(v1, v2)

    # method 2: algebra mathematical
    (pnt1, pnt2) = line
    return (pnt1[1] - pnt2[1]) * point[0] + (pnt2[0] - pnt1[0]) * point[1] + pnt1[0] * pnt2[1] - pnt2[0] * pnt1[1]


def centroid(points):
    """
    :param points: 2D or 3D points list, or ndarray
    :return: centroid point
    """
    points = np.array(points)
    size, rank = points.shape
    if size == 1:
        pnt = points.tolist()
        return pnt[0]

    if rank < 2:
        raise ValueError('Points should be 2D point list or 3D point list')

    xs = points[:, 0]
    ys = points[:, 1]

    if len(points[0]) == 3:
        zs = points[:, 2]
        return [np.mean(xs), np.mean(ys), np.mean(zs)]
    else:
        return [np.mean(xs), np.mean(ys)]


def point_on_line_with_distance(point1, point2, distance=50):
    """
    :param point1: first point of line
    :param point2: second point of line
    :param distance: the distance to second point
    :return:
    """
    x1, y1 = point1
    x2, y2 = point2
    theta = np.arctan2(y2 - y1, x2 - x1)
    y0 = np.sin(theta) * distance + y2
    x0 = np.cos(theta) * distance + x2
    return x0, y0
