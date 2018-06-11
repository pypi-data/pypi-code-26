"""Decorator classes and functions used to throw errors if features aren't set correctly"""
import types

class is_attribute_set(object):
    """test whether or not the db_name attribute has been set"""
    def __init__(self, attribute_name):
        self.attribute_name = attribute_name

    def __call__(self, f):
        def wrapped_f(*args):
            obj = args[0]

            attribute_set = hasattr(obj, self.attribute_name)
            if attribute_set:
                attribute_is_none = not bool(getattr(obj, self.attribute_name))
            else: attribute_is_none = True
            
            if not attribute_set or attribute_is_none:
                raise AttributeError('set the {} attribute first'.format(self.attribute_name))
            return f(*args)
        return wrapped_f

    def __get__(self, instance, objtype):
        return types.MethodType(self, instance)
