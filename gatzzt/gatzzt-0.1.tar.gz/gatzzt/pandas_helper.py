
def diff_unique(x, y):
    x, y = set(x), set(y)
    return x - y, y - x