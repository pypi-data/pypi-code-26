"""Comment 1"""


def print_lol(the_list, indent=False, level=0):
    """Comment 2"""
    for item in the_list:
        if isinstance(item, list):
            print_lol(item, indent, level + 1)
        else:
            if indent:
                for t in range(level):
                    print("\t", end=' ')
            print(item)
