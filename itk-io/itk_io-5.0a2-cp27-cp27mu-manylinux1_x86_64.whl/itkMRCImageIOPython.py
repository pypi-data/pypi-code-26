# This file was automatically generated by SWIG (http://www.swig.org).
# Version 3.0.12
#
# Do not make changes to this file unless you know what you are doing--modify
# the SWIG interface file instead.

from sys import version_info as _swig_python_version_info
if _swig_python_version_info >= (3, 0, 0):
    new_instancemethod = lambda func, inst, cls: _itkMRCImageIOPython.SWIG_PyInstanceMethod_New(func)
else:
    from new import instancemethod as new_instancemethod
if _swig_python_version_info >= (2, 7, 0):
    def swig_import_helper():
        import importlib
        pkg = __name__.rpartition('.')[0]
        mname = '.'.join((pkg, '_itkMRCImageIOPython')).lstrip('.')
        try:
            return importlib.import_module(mname)
        except ImportError:
            return importlib.import_module('_itkMRCImageIOPython')
    _itkMRCImageIOPython = swig_import_helper()
    del swig_import_helper
elif _swig_python_version_info >= (2, 6, 0):
    def swig_import_helper():
        from os.path import dirname
        import imp
        fp = None
        try:
            fp, pathname, description = imp.find_module('_itkMRCImageIOPython', [dirname(__file__)])
        except ImportError:
            import _itkMRCImageIOPython
            return _itkMRCImageIOPython
        try:
            _mod = imp.load_module('_itkMRCImageIOPython', fp, pathname, description)
        finally:
            if fp is not None:
                fp.close()
        return _mod
    _itkMRCImageIOPython = swig_import_helper()
    del swig_import_helper
else:
    import _itkMRCImageIOPython
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

def itkMRCImageIOFactory_New():
  return itkMRCImageIOFactory.New()


def itkMRCImageIO_New():
  return itkMRCImageIO.New()

class itkMRCImageIO(ITKIOImageBaseBasePython.itkStreamingImageIOBase):
    """


    An ImageIO class to read the MRC file format. The MRC file format
    frequently has the extension ".mrc" or ".rec". It is used
    frequently for electron microscopy and is an emerging standard for
    cryo-electron tomography and molecular imaging. The format is used to
    represent 2D, 3D images along with 2D tilt series for tomography.

    The header of the file can contain important information which can not
    be represented in an Image. Therefor the header is placed into the
    MetaDataDictionary of "this". The key to access this is
    MetaDataHeaderName ( fix me when renamed ). See:  MRCHeaderObject
    MetaDataDictionary  This implementation is designed to support IO
    Streaming of arbitrary regions.

    As with all ImageIOs this class is designed to work with
    ImageFileReader and ImageFileWriter, so its direct use is discouraged.

    This code was contributed in the Insight Journal paper: "A Streaming
    IO Base Class and Support for Streaming the MRC and VTK File Format"
    by Lowekamp B., Chen D.http://www.insight-
    journal.org/browse/publication/729https://hdl.handle.net/10380/3171

    See:  ImageFileWriter ImageFileReader ImageIOBase

    C++ includes: itkMRCImageIO.h 
    """

    thisown = _swig_property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc='The membership flag')

    def __init__(self, *args, **kwargs):
        raise AttributeError("No constructor defined")
    __repr__ = _swig_repr

    def __New_orig__():
        """__New_orig__() -> itkMRCImageIO_Pointer"""
        return _itkMRCImageIOPython.itkMRCImageIO___New_orig__()

    __New_orig__ = staticmethod(__New_orig__)

    def Clone(self):
        """Clone(itkMRCImageIO self) -> itkMRCImageIO_Pointer"""
        return _itkMRCImageIOPython.itkMRCImageIO_Clone(self)

    __swig_destroy__ = _itkMRCImageIOPython.delete_itkMRCImageIO

    def cast(obj):
        """cast(itkLightObject obj) -> itkMRCImageIO"""
        return _itkMRCImageIOPython.itkMRCImageIO_cast(obj)

    cast = staticmethod(cast)

    def GetPointer(self):
        """GetPointer(itkMRCImageIO self) -> itkMRCImageIO"""
        return _itkMRCImageIOPython.itkMRCImageIO_GetPointer(self)


    def New(*args, **kargs):
        """New() -> itkMRCImageIO

        Create a new object of the class itkMRCImageIO and set the input and the parameters if some
        named or non-named arguments are passed to that method.

        New() tries to assign all the non named parameters to the input of the new objects - the
        first non named parameter in the first input, etc.

        The named parameters are used by calling the method with the same name prefixed by 'Set'.

        Ex:

          itkMRCImageIO.New( reader, Threshold=10 )

        is (most of the time) equivalent to:

          obj = itkMRCImageIO.New()
          obj.SetInput( 0, reader.GetOutput() )
          obj.SetThreshold( 10 )
        """
        obj = itkMRCImageIO.__New_orig__()
        import itkTemplate
        itkTemplate.New(obj, *args, **kargs)
        return obj
    New = staticmethod(New)

itkMRCImageIO.Clone = new_instancemethod(_itkMRCImageIOPython.itkMRCImageIO_Clone, None, itkMRCImageIO)
itkMRCImageIO.GetPointer = new_instancemethod(_itkMRCImageIOPython.itkMRCImageIO_GetPointer, None, itkMRCImageIO)
itkMRCImageIO_swigregister = _itkMRCImageIOPython.itkMRCImageIO_swigregister
itkMRCImageIO_swigregister(itkMRCImageIO)

def itkMRCImageIO___New_orig__():
    """itkMRCImageIO___New_orig__() -> itkMRCImageIO_Pointer"""
    return _itkMRCImageIOPython.itkMRCImageIO___New_orig__()

def itkMRCImageIO_cast(obj):
    """itkMRCImageIO_cast(itkLightObject obj) -> itkMRCImageIO"""
    return _itkMRCImageIOPython.itkMRCImageIO_cast(obj)

class itkMRCImageIOFactory(ITKCommonBasePython.itkObjectFactoryBase):
    """


    Create instances of MRCImageIO objects using an object factory.

    This code was contributed in the Insight Journal paper: "A Streaming
    IO Base Class and Support for Streaming the MRC and VTK File Format"
    by Lowekamp B., Chen D.http://www.insight-
    journal.org/browse/publication/729https://hdl.handle.net/10380/3171

    C++ includes: itkMRCImageIOFactory.h 
    """

    thisown = _swig_property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc='The membership flag')

    def __init__(self, *args, **kwargs):
        raise AttributeError("No constructor defined")
    __repr__ = _swig_repr

    def __New_orig__():
        """__New_orig__() -> itkMRCImageIOFactory_Pointer"""
        return _itkMRCImageIOPython.itkMRCImageIOFactory___New_orig__()

    __New_orig__ = staticmethod(__New_orig__)

    def RegisterOneFactory():
        """RegisterOneFactory()"""
        return _itkMRCImageIOPython.itkMRCImageIOFactory_RegisterOneFactory()

    RegisterOneFactory = staticmethod(RegisterOneFactory)
    __swig_destroy__ = _itkMRCImageIOPython.delete_itkMRCImageIOFactory

    def cast(obj):
        """cast(itkLightObject obj) -> itkMRCImageIOFactory"""
        return _itkMRCImageIOPython.itkMRCImageIOFactory_cast(obj)

    cast = staticmethod(cast)

    def GetPointer(self):
        """GetPointer(itkMRCImageIOFactory self) -> itkMRCImageIOFactory"""
        return _itkMRCImageIOPython.itkMRCImageIOFactory_GetPointer(self)


    def New(*args, **kargs):
        """New() -> itkMRCImageIOFactory

        Create a new object of the class itkMRCImageIOFactory and set the input and the parameters if some
        named or non-named arguments are passed to that method.

        New() tries to assign all the non named parameters to the input of the new objects - the
        first non named parameter in the first input, etc.

        The named parameters are used by calling the method with the same name prefixed by 'Set'.

        Ex:

          itkMRCImageIOFactory.New( reader, Threshold=10 )

        is (most of the time) equivalent to:

          obj = itkMRCImageIOFactory.New()
          obj.SetInput( 0, reader.GetOutput() )
          obj.SetThreshold( 10 )
        """
        obj = itkMRCImageIOFactory.__New_orig__()
        import itkTemplate
        itkTemplate.New(obj, *args, **kargs)
        return obj
    New = staticmethod(New)

itkMRCImageIOFactory.GetPointer = new_instancemethod(_itkMRCImageIOPython.itkMRCImageIOFactory_GetPointer, None, itkMRCImageIOFactory)
itkMRCImageIOFactory_swigregister = _itkMRCImageIOPython.itkMRCImageIOFactory_swigregister
itkMRCImageIOFactory_swigregister(itkMRCImageIOFactory)

def itkMRCImageIOFactory___New_orig__():
    """itkMRCImageIOFactory___New_orig__() -> itkMRCImageIOFactory_Pointer"""
    return _itkMRCImageIOPython.itkMRCImageIOFactory___New_orig__()

def itkMRCImageIOFactory_RegisterOneFactory():
    """itkMRCImageIOFactory_RegisterOneFactory()"""
    return _itkMRCImageIOPython.itkMRCImageIOFactory_RegisterOneFactory()

def itkMRCImageIOFactory_cast(obj):
    """itkMRCImageIOFactory_cast(itkLightObject obj) -> itkMRCImageIOFactory"""
    return _itkMRCImageIOPython.itkMRCImageIOFactory_cast(obj)



