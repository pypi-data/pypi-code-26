from functools import wraps


def nonexequi(a_func):
    ''' This decorator when apply over def, the def dont work, but return a message informing that skip.

    :param a_func: any function
    :return: str = "Skip: a_function_name"
    '''
    @wraps(a_func)
    def wrap_the_function(self):
        return 'Skip: {}'.format(a_func.__name__)

    return wrap_the_function


# See http://peak.telecommunity.com/DevCenter/setuptools#namespace-packages
try:
    __import__('pkg_resources').declare_namespace(__name__)
except ImportError:
    from pkgutil import extend_path
    __path__ = extend_path(__path__, __name__)
