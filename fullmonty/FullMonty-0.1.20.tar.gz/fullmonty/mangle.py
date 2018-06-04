# coding=utf-8
"""
Function to mangle a name the way python does for leading double underscore names.

From PEP 8::

    If your class is intended to be subclassed, and you have attributes that you do not want
    subclasses to use, consider naming them with double leading underscores and no trailing
    underscores. This invokes Python's name mangling algorithm, where the name of the class
    is mangled into the attribute name. This helps avoid attribute name collisions should
    subclasses inadvertently contain attributes with the same name.


"""

MANGLE_LEN = 256   # magic constant from compile.c


def mangle(name, klass):
    """
    From:  https://stackoverflow.com/questions/11024344/python-name-mangling-function

    >>> mangle('__some_such', 'Foo')
    '_Foo__some_such'

    Here is the function itself (from Python 2.7 source code) in case you just want
    to copy it into your source or verify that your version is equivalent:
    """
    if not name.startswith('__'):
        return name
    if len(name) + 2 >= MANGLE_LEN:
        return name
    if name.endswith('__'):
        return name
    try:
        i = 0
        while klass[i] == '_':
            i = i + 1
    except IndexError:
        return name
    klass = klass[i:]

    tlen = len(klass) + len(name)
    if tlen > MANGLE_LEN:
        klass = klass[:MANGLE_LEN-tlen]

    return "_%s%s" % (klass, name)
