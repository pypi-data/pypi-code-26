# This file was automatically generated by SWIG (http://www.swig.org).
# Version 3.0.12
#
# Do not make changes to this file unless you know what you are doing--modify
# the SWIG interface file instead.

from sys import version_info as _swig_python_version_info
if _swig_python_version_info >= (3, 0, 0):
    new_instancemethod = lambda func, inst, cls: _itkSpatialObjectReaderPython.SWIG_PyInstanceMethod_New(func)
else:
    from new import instancemethod as new_instancemethod
if _swig_python_version_info >= (2, 7, 0):
    def swig_import_helper():
        import importlib
        pkg = __name__.rpartition('.')[0]
        mname = '.'.join((pkg, '_itkSpatialObjectReaderPython')).lstrip('.')
        try:
            return importlib.import_module(mname)
        except ImportError:
            return importlib.import_module('_itkSpatialObjectReaderPython')
    _itkSpatialObjectReaderPython = swig_import_helper()
    del swig_import_helper
elif _swig_python_version_info >= (2, 6, 0):
    def swig_import_helper():
        from os.path import dirname
        import imp
        fp = None
        try:
            fp, pathname, description = imp.find_module('_itkSpatialObjectReaderPython', [dirname(__file__)])
        except ImportError:
            import _itkSpatialObjectReaderPython
            return _itkSpatialObjectReaderPython
        try:
            _mod = imp.load_module('_itkSpatialObjectReaderPython', fp, pathname, description)
        finally:
            if fp is not None:
                fp.close()
        return _mod
    _itkSpatialObjectReaderPython = swig_import_helper()
    del swig_import_helper
else:
    import _itkSpatialObjectReaderPython
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


import itkMetaConverterBasePython
import ITKCommonBasePython
import pyBasePython
import itkSpatialObjectBasePython
import itkIndexPython
import itkSizePython
import itkOffsetPython
import itkImageRegionPython
import itkPointPython
import vnl_vectorPython
import vnl_matrixPython
import stdcomplexPython
import itkFixedArrayPython
import itkVectorPython
import vnl_vector_refPython
import itkBoundingBoxPython
import itkMapContainerPython
import itkVectorContainerPython
import itkContinuousIndexPython
import itkMatrixPython
import vnl_matrix_fixedPython
import itkCovariantVectorPython
import itkAffineGeometryFramePython
import itkScalableAffineTransformPython
import itkTransformBasePython
import itkArrayPython
import itkSymmetricSecondRankTensorPython
import itkVariableLengthVectorPython
import itkArray2DPython
import itkOptimizerParametersPython
import itkDiffusionTensor3DPython
import itkAffineTransformPython
import itkMatrixOffsetTransformBasePython
import itkSpatialObjectPropertyPython
import itkRGBAPixelPython
import itkGroupSpatialObjectPython
import itkSceneSpatialObjectPython

def itkSpatialObjectReader3_New():
  return itkSpatialObjectReader3.New()


def itkSpatialObjectReader2_New():
  return itkSpatialObjectReader2.New()

class itkSpatialObjectReader2(ITKCommonBasePython.itkObject):
    """


    TODO.

    C++ includes: itkSpatialObjectReader.h 
    """

    thisown = _swig_property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc='The membership flag')

    def __init__(self, *args, **kwargs):
        raise AttributeError("No constructor defined")
    __repr__ = _swig_repr

    def __New_orig__() -> "itkSpatialObjectReader2_Pointer":
        """__New_orig__() -> itkSpatialObjectReader2_Pointer"""
        return _itkSpatialObjectReaderPython.itkSpatialObjectReader2___New_orig__()

    __New_orig__ = staticmethod(__New_orig__)

    def Clone(self) -> "itkSpatialObjectReader2_Pointer":
        """Clone(itkSpatialObjectReader2 self) -> itkSpatialObjectReader2_Pointer"""
        return _itkSpatialObjectReaderPython.itkSpatialObjectReader2_Clone(self)


    def Update(self) -> "void":
        """
        Update(itkSpatialObjectReader2 self)

        Load a scene file. 
        """
        return _itkSpatialObjectReaderPython.itkSpatialObjectReader2_Update(self)


    def SetFileName(self, *args) -> "void":
        """
        SetFileName(itkSpatialObjectReader2 self, char const * _arg)
        SetFileName(itkSpatialObjectReader2 self, std::string const & _arg)

        Set the filename 
        """
        return _itkSpatialObjectReaderPython.itkSpatialObjectReader2_SetFileName(self, *args)


    def GetFileName(self) -> "char const *":
        """
        GetFileName(itkSpatialObjectReader2 self) -> char const *

        Get the filename 
        """
        return _itkSpatialObjectReaderPython.itkSpatialObjectReader2_GetFileName(self)


    def GetScene(self) -> "itkSceneSpatialObject2_Pointer":
        """
        GetScene(itkSpatialObjectReader2 self) -> itkSceneSpatialObject2_Pointer

        Get the output 
        """
        return _itkSpatialObjectReaderPython.itkSpatialObjectReader2_GetScene(self)


    def GetGroup(self) -> "itkGroupSpatialObject2_Pointer":
        """GetGroup(itkSpatialObjectReader2 self) -> itkGroupSpatialObject2_Pointer"""
        return _itkSpatialObjectReaderPython.itkSpatialObjectReader2_GetGroup(self)


    def GetEvent(self) -> "itkMetaEvent const *":
        """
        GetEvent(itkSpatialObjectReader2 self) -> itkMetaEvent

        Set/GetEvent 
        """
        return _itkSpatialObjectReaderPython.itkSpatialObjectReader2_GetEvent(self)


    def SetEvent(self, event: 'itkMetaEvent') -> "void":
        """SetEvent(itkSpatialObjectReader2 self, itkMetaEvent event)"""
        return _itkSpatialObjectReaderPython.itkSpatialObjectReader2_SetEvent(self, event)


    def RegisterMetaConverter(self, metaTypeName: 'char const *', spatialObjectTypeName: 'char const *', converter: 'itkMetaConverterBase2') -> "void":
        """
        RegisterMetaConverter(itkSpatialObjectReader2 self, char const * metaTypeName, char const * spatialObjectTypeName, itkMetaConverterBase2 converter)

        Add a
        converter for a new MetaObject/SpatialObject type 
        """
        return _itkSpatialObjectReaderPython.itkSpatialObjectReader2_RegisterMetaConverter(self, metaTypeName, spatialObjectTypeName, converter)

    __swig_destroy__ = _itkSpatialObjectReaderPython.delete_itkSpatialObjectReader2

    def cast(obj: 'itkLightObject') -> "itkSpatialObjectReader2 *":
        """cast(itkLightObject obj) -> itkSpatialObjectReader2"""
        return _itkSpatialObjectReaderPython.itkSpatialObjectReader2_cast(obj)

    cast = staticmethod(cast)

    def GetPointer(self) -> "itkSpatialObjectReader2 *":
        """GetPointer(itkSpatialObjectReader2 self) -> itkSpatialObjectReader2"""
        return _itkSpatialObjectReaderPython.itkSpatialObjectReader2_GetPointer(self)


    def New(*args, **kargs):
        """New() -> itkSpatialObjectReader2

        Create a new object of the class itkSpatialObjectReader2 and set the input and the parameters if some
        named or non-named arguments are passed to that method.

        New() tries to assign all the non named parameters to the input of the new objects - the
        first non named parameter in the first input, etc.

        The named parameters are used by calling the method with the same name prefixed by 'Set'.

        Ex:

          itkSpatialObjectReader2.New( reader, Threshold=10 )

        is (most of the time) equivalent to:

          obj = itkSpatialObjectReader2.New()
          obj.SetInput( 0, reader.GetOutput() )
          obj.SetThreshold( 10 )
        """
        obj = itkSpatialObjectReader2.__New_orig__()
        import itkTemplate
        itkTemplate.New(obj, *args, **kargs)
        return obj
    New = staticmethod(New)

itkSpatialObjectReader2.Clone = new_instancemethod(_itkSpatialObjectReaderPython.itkSpatialObjectReader2_Clone, None, itkSpatialObjectReader2)
itkSpatialObjectReader2.Update = new_instancemethod(_itkSpatialObjectReaderPython.itkSpatialObjectReader2_Update, None, itkSpatialObjectReader2)
itkSpatialObjectReader2.SetFileName = new_instancemethod(_itkSpatialObjectReaderPython.itkSpatialObjectReader2_SetFileName, None, itkSpatialObjectReader2)
itkSpatialObjectReader2.GetFileName = new_instancemethod(_itkSpatialObjectReaderPython.itkSpatialObjectReader2_GetFileName, None, itkSpatialObjectReader2)
itkSpatialObjectReader2.GetScene = new_instancemethod(_itkSpatialObjectReaderPython.itkSpatialObjectReader2_GetScene, None, itkSpatialObjectReader2)
itkSpatialObjectReader2.GetGroup = new_instancemethod(_itkSpatialObjectReaderPython.itkSpatialObjectReader2_GetGroup, None, itkSpatialObjectReader2)
itkSpatialObjectReader2.GetEvent = new_instancemethod(_itkSpatialObjectReaderPython.itkSpatialObjectReader2_GetEvent, None, itkSpatialObjectReader2)
itkSpatialObjectReader2.SetEvent = new_instancemethod(_itkSpatialObjectReaderPython.itkSpatialObjectReader2_SetEvent, None, itkSpatialObjectReader2)
itkSpatialObjectReader2.RegisterMetaConverter = new_instancemethod(_itkSpatialObjectReaderPython.itkSpatialObjectReader2_RegisterMetaConverter, None, itkSpatialObjectReader2)
itkSpatialObjectReader2.GetPointer = new_instancemethod(_itkSpatialObjectReaderPython.itkSpatialObjectReader2_GetPointer, None, itkSpatialObjectReader2)
itkSpatialObjectReader2_swigregister = _itkSpatialObjectReaderPython.itkSpatialObjectReader2_swigregister
itkSpatialObjectReader2_swigregister(itkSpatialObjectReader2)

def itkSpatialObjectReader2___New_orig__() -> "itkSpatialObjectReader2_Pointer":
    """itkSpatialObjectReader2___New_orig__() -> itkSpatialObjectReader2_Pointer"""
    return _itkSpatialObjectReaderPython.itkSpatialObjectReader2___New_orig__()

def itkSpatialObjectReader2_cast(obj: 'itkLightObject') -> "itkSpatialObjectReader2 *":
    """itkSpatialObjectReader2_cast(itkLightObject obj) -> itkSpatialObjectReader2"""
    return _itkSpatialObjectReaderPython.itkSpatialObjectReader2_cast(obj)

class itkSpatialObjectReader3(ITKCommonBasePython.itkObject):
    """


    TODO.

    C++ includes: itkSpatialObjectReader.h 
    """

    thisown = _swig_property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc='The membership flag')

    def __init__(self, *args, **kwargs):
        raise AttributeError("No constructor defined")
    __repr__ = _swig_repr

    def __New_orig__() -> "itkSpatialObjectReader3_Pointer":
        """__New_orig__() -> itkSpatialObjectReader3_Pointer"""
        return _itkSpatialObjectReaderPython.itkSpatialObjectReader3___New_orig__()

    __New_orig__ = staticmethod(__New_orig__)

    def Clone(self) -> "itkSpatialObjectReader3_Pointer":
        """Clone(itkSpatialObjectReader3 self) -> itkSpatialObjectReader3_Pointer"""
        return _itkSpatialObjectReaderPython.itkSpatialObjectReader3_Clone(self)


    def Update(self) -> "void":
        """
        Update(itkSpatialObjectReader3 self)

        Load a scene file. 
        """
        return _itkSpatialObjectReaderPython.itkSpatialObjectReader3_Update(self)


    def SetFileName(self, *args) -> "void":
        """
        SetFileName(itkSpatialObjectReader3 self, char const * _arg)
        SetFileName(itkSpatialObjectReader3 self, std::string const & _arg)

        Set the filename 
        """
        return _itkSpatialObjectReaderPython.itkSpatialObjectReader3_SetFileName(self, *args)


    def GetFileName(self) -> "char const *":
        """
        GetFileName(itkSpatialObjectReader3 self) -> char const *

        Get the filename 
        """
        return _itkSpatialObjectReaderPython.itkSpatialObjectReader3_GetFileName(self)


    def GetScene(self) -> "itkSceneSpatialObject3_Pointer":
        """
        GetScene(itkSpatialObjectReader3 self) -> itkSceneSpatialObject3_Pointer

        Get the output 
        """
        return _itkSpatialObjectReaderPython.itkSpatialObjectReader3_GetScene(self)


    def GetGroup(self) -> "itkGroupSpatialObject3_Pointer":
        """GetGroup(itkSpatialObjectReader3 self) -> itkGroupSpatialObject3_Pointer"""
        return _itkSpatialObjectReaderPython.itkSpatialObjectReader3_GetGroup(self)


    def GetEvent(self) -> "itkMetaEvent const *":
        """
        GetEvent(itkSpatialObjectReader3 self) -> itkMetaEvent

        Set/GetEvent 
        """
        return _itkSpatialObjectReaderPython.itkSpatialObjectReader3_GetEvent(self)


    def SetEvent(self, event: 'itkMetaEvent') -> "void":
        """SetEvent(itkSpatialObjectReader3 self, itkMetaEvent event)"""
        return _itkSpatialObjectReaderPython.itkSpatialObjectReader3_SetEvent(self, event)


    def RegisterMetaConverter(self, metaTypeName: 'char const *', spatialObjectTypeName: 'char const *', converter: 'itkMetaConverterBase3') -> "void":
        """
        RegisterMetaConverter(itkSpatialObjectReader3 self, char const * metaTypeName, char const * spatialObjectTypeName, itkMetaConverterBase3 converter)

        Add a
        converter for a new MetaObject/SpatialObject type 
        """
        return _itkSpatialObjectReaderPython.itkSpatialObjectReader3_RegisterMetaConverter(self, metaTypeName, spatialObjectTypeName, converter)

    __swig_destroy__ = _itkSpatialObjectReaderPython.delete_itkSpatialObjectReader3

    def cast(obj: 'itkLightObject') -> "itkSpatialObjectReader3 *":
        """cast(itkLightObject obj) -> itkSpatialObjectReader3"""
        return _itkSpatialObjectReaderPython.itkSpatialObjectReader3_cast(obj)

    cast = staticmethod(cast)

    def GetPointer(self) -> "itkSpatialObjectReader3 *":
        """GetPointer(itkSpatialObjectReader3 self) -> itkSpatialObjectReader3"""
        return _itkSpatialObjectReaderPython.itkSpatialObjectReader3_GetPointer(self)


    def New(*args, **kargs):
        """New() -> itkSpatialObjectReader3

        Create a new object of the class itkSpatialObjectReader3 and set the input and the parameters if some
        named or non-named arguments are passed to that method.

        New() tries to assign all the non named parameters to the input of the new objects - the
        first non named parameter in the first input, etc.

        The named parameters are used by calling the method with the same name prefixed by 'Set'.

        Ex:

          itkSpatialObjectReader3.New( reader, Threshold=10 )

        is (most of the time) equivalent to:

          obj = itkSpatialObjectReader3.New()
          obj.SetInput( 0, reader.GetOutput() )
          obj.SetThreshold( 10 )
        """
        obj = itkSpatialObjectReader3.__New_orig__()
        import itkTemplate
        itkTemplate.New(obj, *args, **kargs)
        return obj
    New = staticmethod(New)

itkSpatialObjectReader3.Clone = new_instancemethod(_itkSpatialObjectReaderPython.itkSpatialObjectReader3_Clone, None, itkSpatialObjectReader3)
itkSpatialObjectReader3.Update = new_instancemethod(_itkSpatialObjectReaderPython.itkSpatialObjectReader3_Update, None, itkSpatialObjectReader3)
itkSpatialObjectReader3.SetFileName = new_instancemethod(_itkSpatialObjectReaderPython.itkSpatialObjectReader3_SetFileName, None, itkSpatialObjectReader3)
itkSpatialObjectReader3.GetFileName = new_instancemethod(_itkSpatialObjectReaderPython.itkSpatialObjectReader3_GetFileName, None, itkSpatialObjectReader3)
itkSpatialObjectReader3.GetScene = new_instancemethod(_itkSpatialObjectReaderPython.itkSpatialObjectReader3_GetScene, None, itkSpatialObjectReader3)
itkSpatialObjectReader3.GetGroup = new_instancemethod(_itkSpatialObjectReaderPython.itkSpatialObjectReader3_GetGroup, None, itkSpatialObjectReader3)
itkSpatialObjectReader3.GetEvent = new_instancemethod(_itkSpatialObjectReaderPython.itkSpatialObjectReader3_GetEvent, None, itkSpatialObjectReader3)
itkSpatialObjectReader3.SetEvent = new_instancemethod(_itkSpatialObjectReaderPython.itkSpatialObjectReader3_SetEvent, None, itkSpatialObjectReader3)
itkSpatialObjectReader3.RegisterMetaConverter = new_instancemethod(_itkSpatialObjectReaderPython.itkSpatialObjectReader3_RegisterMetaConverter, None, itkSpatialObjectReader3)
itkSpatialObjectReader3.GetPointer = new_instancemethod(_itkSpatialObjectReaderPython.itkSpatialObjectReader3_GetPointer, None, itkSpatialObjectReader3)
itkSpatialObjectReader3_swigregister = _itkSpatialObjectReaderPython.itkSpatialObjectReader3_swigregister
itkSpatialObjectReader3_swigregister(itkSpatialObjectReader3)

def itkSpatialObjectReader3___New_orig__() -> "itkSpatialObjectReader3_Pointer":
    """itkSpatialObjectReader3___New_orig__() -> itkSpatialObjectReader3_Pointer"""
    return _itkSpatialObjectReaderPython.itkSpatialObjectReader3___New_orig__()

def itkSpatialObjectReader3_cast(obj: 'itkLightObject') -> "itkSpatialObjectReader3 *":
    """itkSpatialObjectReader3_cast(itkLightObject obj) -> itkSpatialObjectReader3"""
    return _itkSpatialObjectReaderPython.itkSpatialObjectReader3_cast(obj)



