from functools import wraps
from os.path import abspath, join, dirname

__version__ = open(abspath(join(dirname(__file__), 'version.txt'))).read().strip()


def nonexequi(a_func):
    ''' This decorator when apply over def, the def dont work, but return a message informing that skip.

    :param a_func: any function
    :return: str = "Skip: a_function_name"
    '''
    @wraps(a_func)
    def wrap_the_function(self):
        return 'Skip: {}'.format(a_func.__name__)

    return wrap_the_function

