import os
_ROOT = os.path.abspath(os.path.dirname(__file__))


def get_data():
    foo_config = open(
        os.path.join(os.path.dirname(__file__), "data.data.txt")
    ).read()
    print(os.path.join(os.path.dirname(__file__), "data.data.txt"))
    return foo_config
    # return os.path.join(_ROOT, 'data', path)


print(get_data())
