# This file was automatically generated by SWIG (http://www.swig.org).
# Version 3.0.12
#
# Do not make changes to this file unless you know what you are doing--modify
# the SWIG interface file instead.

from sys import version_info as _swig_python_version_info
if _swig_python_version_info >= (3, 0, 0):
    new_instancemethod = lambda func, inst, cls: _itkSiemensVisionImageIOPython.SWIG_PyInstanceMethod_New(func)
else:
    from new import instancemethod as new_instancemethod
if _swig_python_version_info >= (2, 7, 0):
    def swig_import_helper():
        import importlib
        pkg = __name__.rpartition('.')[0]
        mname = '.'.join((pkg, '_itkSiemensVisionImageIOPython')).lstrip('.')
        try:
            return importlib.import_module(mname)
        except ImportError:
            return importlib.import_module('_itkSiemensVisionImageIOPython')
    _itkSiemensVisionImageIOPython = swig_import_helper()
    del swig_import_helper
elif _swig_python_version_info >= (2, 6, 0):
    def swig_import_helper():
        from os.path import dirname
        import imp
        fp = None
        try:
            fp, pathname, description = imp.find_module('_itkSiemensVisionImageIOPython', [dirname(__file__)])
        except ImportError:
            import _itkSiemensVisionImageIOPython
            return _itkSiemensVisionImageIOPython
        try:
            _mod = imp.load_module('_itkSiemensVisionImageIOPython', fp, pathname, description)
        finally:
            if fp is not None:
                fp.close()
        return _mod
    _itkSiemensVisionImageIOPython = swig_import_helper()
    del swig_import_helper
else:
    import _itkSiemensVisionImageIOPython
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


import itkIPLCommonImageIOPython
import ITKIOImageBaseBasePython
import ITKCommonBasePython
import pyBasePython
import vnl_vectorPython
import vnl_matrixPython
import stdcomplexPython

def itkSiemensVisionImageIOFactory_New():
  return itkSiemensVisionImageIOFactory.New()


def itkSiemensVisionImageIO_New():
  return itkSiemensVisionImageIO.New()

class itkSiemensVisionImageIO(itkIPLCommonImageIOPython.itkIPLCommonImageIO):
    """


    Class that defines how to read SiemensVision file format.

    Hans J. Johnson

    C++ includes: itkSiemensVisionImageIO.h 
    """

    thisown = _swig_property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc='The membership flag')

    def __init__(self, *args, **kwargs):
        raise AttributeError("No constructor defined")
    __repr__ = _swig_repr

    def __New_orig__() -> "itkSiemensVisionImageIO_Pointer":
        """__New_orig__() -> itkSiemensVisionImageIO_Pointer"""
        return _itkSiemensVisionImageIOPython.itkSiemensVisionImageIO___New_orig__()

    __New_orig__ = staticmethod(__New_orig__)

    def Clone(self) -> "itkSiemensVisionImageIO_Pointer":
        """Clone(itkSiemensVisionImageIO self) -> itkSiemensVisionImageIO_Pointer"""
        return _itkSiemensVisionImageIOPython.itkSiemensVisionImageIO_Clone(self)

    __swig_destroy__ = _itkSiemensVisionImageIOPython.delete_itkSiemensVisionImageIO

    def cast(obj: 'itkLightObject') -> "itkSiemensVisionImageIO *":
        """cast(itkLightObject obj) -> itkSiemensVisionImageIO"""
        return _itkSiemensVisionImageIOPython.itkSiemensVisionImageIO_cast(obj)

    cast = staticmethod(cast)

    def GetPointer(self) -> "itkSiemensVisionImageIO *":
        """GetPointer(itkSiemensVisionImageIO self) -> itkSiemensVisionImageIO"""
        return _itkSiemensVisionImageIOPython.itkSiemensVisionImageIO_GetPointer(self)


    def New(*args, **kargs):
        """New() -> itkSiemensVisionImageIO

        Create a new object of the class itkSiemensVisionImageIO and set the input and the parameters if some
        named or non-named arguments are passed to that method.

        New() tries to assign all the non named parameters to the input of the new objects - the
        first non named parameter in the first input, etc.

        The named parameters are used by calling the method with the same name prefixed by 'Set'.

        Ex:

          itkSiemensVisionImageIO.New( reader, Threshold=10 )

        is (most of the time) equivalent to:

          obj = itkSiemensVisionImageIO.New()
          obj.SetInput( 0, reader.GetOutput() )
          obj.SetThreshold( 10 )
        """
        obj = itkSiemensVisionImageIO.__New_orig__()
        import itkTemplate
        itkTemplate.New(obj, *args, **kargs)
        return obj
    New = staticmethod(New)

itkSiemensVisionImageIO.Clone = new_instancemethod(_itkSiemensVisionImageIOPython.itkSiemensVisionImageIO_Clone, None, itkSiemensVisionImageIO)
itkSiemensVisionImageIO.GetPointer = new_instancemethod(_itkSiemensVisionImageIOPython.itkSiemensVisionImageIO_GetPointer, None, itkSiemensVisionImageIO)
itkSiemensVisionImageIO_swigregister = _itkSiemensVisionImageIOPython.itkSiemensVisionImageIO_swigregister
itkSiemensVisionImageIO_swigregister(itkSiemensVisionImageIO)

def itkSiemensVisionImageIO___New_orig__() -> "itkSiemensVisionImageIO_Pointer":
    """itkSiemensVisionImageIO___New_orig__() -> itkSiemensVisionImageIO_Pointer"""
    return _itkSiemensVisionImageIOPython.itkSiemensVisionImageIO___New_orig__()

def itkSiemensVisionImageIO_cast(obj: 'itkLightObject') -> "itkSiemensVisionImageIO *":
    """itkSiemensVisionImageIO_cast(itkLightObject obj) -> itkSiemensVisionImageIO"""
    return _itkSiemensVisionImageIOPython.itkSiemensVisionImageIO_cast(obj)

class itkSiemensVisionImageIOFactory(ITKCommonBasePython.itkObjectFactoryBase):
    """


    Create instances of SiemensVisionImageIO objects using an object
    factory.

    C++ includes: itkSiemensVisionImageIOFactory.h 
    """

    thisown = _swig_property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc='The membership flag')

    def __init__(self, *args, **kwargs):
        raise AttributeError("No constructor defined")
    __repr__ = _swig_repr

    def __New_orig__() -> "itkSiemensVisionImageIOFactory_Pointer":
        """__New_orig__() -> itkSiemensVisionImageIOFactory_Pointer"""
        return _itkSiemensVisionImageIOPython.itkSiemensVisionImageIOFactory___New_orig__()

    __New_orig__ = staticmethod(__New_orig__)

    def RegisterOneFactory() -> "void":
        """RegisterOneFactory()"""
        return _itkSiemensVisionImageIOPython.itkSiemensVisionImageIOFactory_RegisterOneFactory()

    RegisterOneFactory = staticmethod(RegisterOneFactory)
    __swig_destroy__ = _itkSiemensVisionImageIOPython.delete_itkSiemensVisionImageIOFactory

    def cast(obj: 'itkLightObject') -> "itkSiemensVisionImageIOFactory *":
        """cast(itkLightObject obj) -> itkSiemensVisionImageIOFactory"""
        return _itkSiemensVisionImageIOPython.itkSiemensVisionImageIOFactory_cast(obj)

    cast = staticmethod(cast)

    def GetPointer(self) -> "itkSiemensVisionImageIOFactory *":
        """GetPointer(itkSiemensVisionImageIOFactory self) -> itkSiemensVisionImageIOFactory"""
        return _itkSiemensVisionImageIOPython.itkSiemensVisionImageIOFactory_GetPointer(self)


    def New(*args, **kargs):
        """New() -> itkSiemensVisionImageIOFactory

        Create a new object of the class itkSiemensVisionImageIOFactory and set the input and the parameters if some
        named or non-named arguments are passed to that method.

        New() tries to assign all the non named parameters to the input of the new objects - the
        first non named parameter in the first input, etc.

        The named parameters are used by calling the method with the same name prefixed by 'Set'.

        Ex:

          itkSiemensVisionImageIOFactory.New( reader, Threshold=10 )

        is (most of the time) equivalent to:

          obj = itkSiemensVisionImageIOFactory.New()
          obj.SetInput( 0, reader.GetOutput() )
          obj.SetThreshold( 10 )
        """
        obj = itkSiemensVisionImageIOFactory.__New_orig__()
        import itkTemplate
        itkTemplate.New(obj, *args, **kargs)
        return obj
    New = staticmethod(New)

itkSiemensVisionImageIOFactory.GetPointer = new_instancemethod(_itkSiemensVisionImageIOPython.itkSiemensVisionImageIOFactory_GetPointer, None, itkSiemensVisionImageIOFactory)
itkSiemensVisionImageIOFactory_swigregister = _itkSiemensVisionImageIOPython.itkSiemensVisionImageIOFactory_swigregister
itkSiemensVisionImageIOFactory_swigregister(itkSiemensVisionImageIOFactory)

def itkSiemensVisionImageIOFactory___New_orig__() -> "itkSiemensVisionImageIOFactory_Pointer":
    """itkSiemensVisionImageIOFactory___New_orig__() -> itkSiemensVisionImageIOFactory_Pointer"""
    return _itkSiemensVisionImageIOPython.itkSiemensVisionImageIOFactory___New_orig__()

def itkSiemensVisionImageIOFactory_RegisterOneFactory() -> "void":
    """itkSiemensVisionImageIOFactory_RegisterOneFactory()"""
    return _itkSiemensVisionImageIOPython.itkSiemensVisionImageIOFactory_RegisterOneFactory()

def itkSiemensVisionImageIOFactory_cast(obj: 'itkLightObject') -> "itkSiemensVisionImageIOFactory *":
    """itkSiemensVisionImageIOFactory_cast(itkLightObject obj) -> itkSiemensVisionImageIOFactory"""
    return _itkSiemensVisionImageIOPython.itkSiemensVisionImageIOFactory_cast(obj)



