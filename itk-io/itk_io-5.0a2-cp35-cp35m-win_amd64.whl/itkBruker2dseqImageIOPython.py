# This file was automatically generated by SWIG (http://www.swig.org).
# Version 3.0.12
#
# Do not make changes to this file unless you know what you are doing--modify
# the SWIG interface file instead.

from sys import version_info as _swig_python_version_info
if _swig_python_version_info >= (3, 0, 0):
    new_instancemethod = lambda func, inst, cls: _itkBruker2dseqImageIOPython.SWIG_PyInstanceMethod_New(func)
else:
    from new import instancemethod as new_instancemethod
if _swig_python_version_info >= (2, 7, 0):
    def swig_import_helper():
        import importlib
        pkg = __name__.rpartition('.')[0]
        mname = '.'.join((pkg, '_itkBruker2dseqImageIOPython')).lstrip('.')
        try:
            return importlib.import_module(mname)
        except ImportError:
            return importlib.import_module('_itkBruker2dseqImageIOPython')
    _itkBruker2dseqImageIOPython = swig_import_helper()
    del swig_import_helper
elif _swig_python_version_info >= (2, 6, 0):
    def swig_import_helper():
        from os.path import dirname
        import imp
        fp = None
        try:
            fp, pathname, description = imp.find_module('_itkBruker2dseqImageIOPython', [dirname(__file__)])
        except ImportError:
            import _itkBruker2dseqImageIOPython
            return _itkBruker2dseqImageIOPython
        try:
            _mod = imp.load_module('_itkBruker2dseqImageIOPython', fp, pathname, description)
        finally:
            if fp is not None:
                fp.close()
        return _mod
    _itkBruker2dseqImageIOPython = swig_import_helper()
    del swig_import_helper
else:
    import _itkBruker2dseqImageIOPython
del _swig_python_version_info

try:
    _swig_property = property
except NameError:
    pass  # Python < 2.2 doesn't have 'property'.

try:
    import builtins as __builtin__
except ImportError:
    import __builtin__

def _swig_setattr_nondynamic(self, class_type, name, value, static=1):
    if (name == "thisown"):
        return self.this.own(value)
    if (name == "this"):
        if type(value).__name__ == 'SwigPyObject':
            self.__dict__[name] = value
            return
    method = class_type.__swig_setmethods__.get(name, None)
    if method:
        return method(self, value)
    if (not static):
        object.__setattr__(self, name, value)
    else:
        raise AttributeError("You cannot add attributes to %s" % self)


def _swig_setattr(self, class_type, name, value):
    return _swig_setattr_nondynamic(self, class_type, name, value, 0)


def _swig_getattr(self, class_type, name):
    if (name == "thisown"):
        return self.this.own()
    method = class_type.__swig_getmethods__.get(name, None)
    if method:
        return method(self)
    raise AttributeError("'%s' object has no attribute '%s'" % (class_type.__name__, name))


def _swig_repr(self):
    try:
        strthis = "proxy of " + self.this.__repr__()
    except __builtin__.Exception:
        strthis = ""
    return "<%s.%s; %s >" % (self.__class__.__module__, self.__class__.__name__, strthis,)


def _swig_setattr_nondynamic_method(set):
    def set_attr(self, name, value):
        if (name == "thisown"):
            return self.this.own(value)
        if hasattr(self, name) or (name == "this"):
            set(self, name, value)
        else:
            raise AttributeError("You cannot add attributes to %s" % self)
    return set_attr


import ITKIOImageBaseBasePython
import ITKCommonBasePython
import pyBasePython
import vnl_vectorPython
import stdcomplexPython
import vnl_matrixPython

def itkBruker2dseqImageIOFactory_New():
  return itkBruker2dseqImageIOFactory.New()


def itkBruker2dseqImageIO_New():
  return itkBruker2dseqImageIO.New()

class itkBruker2dseqImageIO(ITKIOImageBaseBasePython.itkImageIOBase):
    """Proxy of C++ itkBruker2dseqImageIO class."""

    thisown = _swig_property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc='The membership flag')

    def __init__(self, *args, **kwargs):
        raise AttributeError("No constructor defined")
    __repr__ = _swig_repr

    def __New_orig__() -> "itkBruker2dseqImageIO_Pointer":
        """__New_orig__() -> itkBruker2dseqImageIO_Pointer"""
        return _itkBruker2dseqImageIOPython.itkBruker2dseqImageIO___New_orig__()

    __New_orig__ = staticmethod(__New_orig__)

    def Clone(self) -> "itkBruker2dseqImageIO_Pointer":
        """Clone(itkBruker2dseqImageIO self) -> itkBruker2dseqImageIO_Pointer"""
        return _itkBruker2dseqImageIOPython.itkBruker2dseqImageIO_Clone(self)

    __swig_destroy__ = _itkBruker2dseqImageIOPython.delete_itkBruker2dseqImageIO

    def cast(obj: 'itkLightObject') -> "itkBruker2dseqImageIO *":
        """cast(itkLightObject obj) -> itkBruker2dseqImageIO"""
        return _itkBruker2dseqImageIOPython.itkBruker2dseqImageIO_cast(obj)

    cast = staticmethod(cast)

    def GetPointer(self) -> "itkBruker2dseqImageIO *":
        """GetPointer(itkBruker2dseqImageIO self) -> itkBruker2dseqImageIO"""
        return _itkBruker2dseqImageIOPython.itkBruker2dseqImageIO_GetPointer(self)


    def New(*args, **kargs):
        """New() -> itkBruker2dseqImageIO

        Create a new object of the class itkBruker2dseqImageIO and set the input and the parameters if some
        named or non-named arguments are passed to that method.

        New() tries to assign all the non named parameters to the input of the new objects - the
        first non named parameter in the first input, etc.

        The named parameters are used by calling the method with the same name prefixed by 'Set'.

        Ex:

          itkBruker2dseqImageIO.New( reader, Threshold=10 )

        is (most of the time) equivalent to:

          obj = itkBruker2dseqImageIO.New()
          obj.SetInput( 0, reader.GetOutput() )
          obj.SetThreshold( 10 )
        """
        obj = itkBruker2dseqImageIO.__New_orig__()
        import itkTemplate
        itkTemplate.New(obj, *args, **kargs)
        return obj
    New = staticmethod(New)

itkBruker2dseqImageIO.Clone = new_instancemethod(_itkBruker2dseqImageIOPython.itkBruker2dseqImageIO_Clone, None, itkBruker2dseqImageIO)
itkBruker2dseqImageIO.GetPointer = new_instancemethod(_itkBruker2dseqImageIOPython.itkBruker2dseqImageIO_GetPointer, None, itkBruker2dseqImageIO)
itkBruker2dseqImageIO_swigregister = _itkBruker2dseqImageIOPython.itkBruker2dseqImageIO_swigregister
itkBruker2dseqImageIO_swigregister(itkBruker2dseqImageIO)

def itkBruker2dseqImageIO___New_orig__() -> "itkBruker2dseqImageIO_Pointer":
    """itkBruker2dseqImageIO___New_orig__() -> itkBruker2dseqImageIO_Pointer"""
    return _itkBruker2dseqImageIOPython.itkBruker2dseqImageIO___New_orig__()

def itkBruker2dseqImageIO_cast(obj: 'itkLightObject') -> "itkBruker2dseqImageIO *":
    """itkBruker2dseqImageIO_cast(itkLightObject obj) -> itkBruker2dseqImageIO"""
    return _itkBruker2dseqImageIOPython.itkBruker2dseqImageIO_cast(obj)

class itkBruker2dseqImageIOFactory(ITKCommonBasePython.itkObjectFactoryBase):
    """Proxy of C++ itkBruker2dseqImageIOFactory class."""

    thisown = _swig_property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc='The membership flag')

    def __init__(self, *args, **kwargs):
        raise AttributeError("No constructor defined")
    __repr__ = _swig_repr

    def __New_orig__() -> "itkBruker2dseqImageIOFactory_Pointer":
        """__New_orig__() -> itkBruker2dseqImageIOFactory_Pointer"""
        return _itkBruker2dseqImageIOPython.itkBruker2dseqImageIOFactory___New_orig__()

    __New_orig__ = staticmethod(__New_orig__)

    def RegisterOneFactory() -> "void":
        """RegisterOneFactory()"""
        return _itkBruker2dseqImageIOPython.itkBruker2dseqImageIOFactory_RegisterOneFactory()

    RegisterOneFactory = staticmethod(RegisterOneFactory)
    __swig_destroy__ = _itkBruker2dseqImageIOPython.delete_itkBruker2dseqImageIOFactory

    def cast(obj: 'itkLightObject') -> "itkBruker2dseqImageIOFactory *":
        """cast(itkLightObject obj) -> itkBruker2dseqImageIOFactory"""
        return _itkBruker2dseqImageIOPython.itkBruker2dseqImageIOFactory_cast(obj)

    cast = staticmethod(cast)

    def GetPointer(self) -> "itkBruker2dseqImageIOFactory *":
        """GetPointer(itkBruker2dseqImageIOFactory self) -> itkBruker2dseqImageIOFactory"""
        return _itkBruker2dseqImageIOPython.itkBruker2dseqImageIOFactory_GetPointer(self)


    def New(*args, **kargs):
        """New() -> itkBruker2dseqImageIOFactory

        Create a new object of the class itkBruker2dseqImageIOFactory and set the input and the parameters if some
        named or non-named arguments are passed to that method.

        New() tries to assign all the non named parameters to the input of the new objects - the
        first non named parameter in the first input, etc.

        The named parameters are used by calling the method with the same name prefixed by 'Set'.

        Ex:

          itkBruker2dseqImageIOFactory.New( reader, Threshold=10 )

        is (most of the time) equivalent to:

          obj = itkBruker2dseqImageIOFactory.New()
          obj.SetInput( 0, reader.GetOutput() )
          obj.SetThreshold( 10 )
        """
        obj = itkBruker2dseqImageIOFactory.__New_orig__()
        import itkTemplate
        itkTemplate.New(obj, *args, **kargs)
        return obj
    New = staticmethod(New)

itkBruker2dseqImageIOFactory.GetPointer = new_instancemethod(_itkBruker2dseqImageIOPython.itkBruker2dseqImageIOFactory_GetPointer, None, itkBruker2dseqImageIOFactory)
itkBruker2dseqImageIOFactory_swigregister = _itkBruker2dseqImageIOPython.itkBruker2dseqImageIOFactory_swigregister
itkBruker2dseqImageIOFactory_swigregister(itkBruker2dseqImageIOFactory)

def itkBruker2dseqImageIOFactory___New_orig__() -> "itkBruker2dseqImageIOFactory_Pointer":
    """itkBruker2dseqImageIOFactory___New_orig__() -> itkBruker2dseqImageIOFactory_Pointer"""
    return _itkBruker2dseqImageIOPython.itkBruker2dseqImageIOFactory___New_orig__()

def itkBruker2dseqImageIOFactory_RegisterOneFactory() -> "void":
    """itkBruker2dseqImageIOFactory_RegisterOneFactory()"""
    return _itkBruker2dseqImageIOPython.itkBruker2dseqImageIOFactory_RegisterOneFactory()

def itkBruker2dseqImageIOFactory_cast(obj: 'itkLightObject') -> "itkBruker2dseqImageIOFactory *":
    """itkBruker2dseqImageIOFactory_cast(itkLightObject obj) -> itkBruker2dseqImageIOFactory"""
    return _itkBruker2dseqImageIOPython.itkBruker2dseqImageIOFactory_cast(obj)



