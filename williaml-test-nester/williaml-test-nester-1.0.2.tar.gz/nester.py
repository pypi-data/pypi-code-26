"""Comment 1"""


def print_lol(the_list, level):
    """Comment 2"""
    for item in the_list:
        if isinstance(item, list):
            print_lol(item)
        else:
            for t in range(level):
                print("\t", end='')
            print(item)
