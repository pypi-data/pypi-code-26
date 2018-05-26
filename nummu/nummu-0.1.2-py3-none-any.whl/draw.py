WHITE = (255, 255, 255)

def line(pallete, color, x1, y1, x2, y2, *args):
    if len(args) % 2 != 0:
        raise TypeError('invalid additional points.')
    points = [(x1, y1), (x2, y2), ] + list(args)
    for (a1, b1), (a2, b2) in zip(points[:-1], points[1:]):
        print(a1, b1, a2, b2, color)
        if isinstance(color, int):
            pallete[a1:a2, b1:b2, :] = color
        else:
            for r, g, b in color:
                pallete[a1:a2, b1:b2, 0] = r
                pallete[a1:a2, b1:b2, 1] = g
                pallete[a1:a2, b1:b2, 2] = b
