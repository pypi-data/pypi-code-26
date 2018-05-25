"""Comment 1"""


def print_lol(the_list):
    """Comment 2"""
    for item in the_list:
        if isinstance(item, list):
            print_lol(item)
        else:
            print(item)
