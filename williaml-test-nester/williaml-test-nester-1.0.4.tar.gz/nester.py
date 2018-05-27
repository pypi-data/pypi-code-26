"""Comment 1"""


def print_lol(the_list, level=0):
    """Comment 2"""
    for item in the_list:
        if isinstance(item, list):
            print_lol(item, level)
        else:
            for t in range(level):
                print("\t", end='')
            print(item)
