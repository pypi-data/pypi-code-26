# coding=utf-8

"""
Test name mangling

"""
import inspect
import sys

from fullmonty.mangle import mangle


class managled_class(object):
    __mangled_module_attribute = 5

    def __mangled_method(self):
        pass


# def this_module():
#     caller = inspect.currentframe().f_back
#     name = caller.f_globals['__name__']
#     print(name)
#     return name


def test_module_mangling():
    class_attribute_name = mangle('__mangled_module_attribute', 'managled_class')
    print("\nclass attribute name: \"{name}\"".format(name=class_attribute_name))
