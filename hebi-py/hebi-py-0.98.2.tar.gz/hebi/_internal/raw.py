# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
#
#  HEBI Core python API - Copyright 2018 HEBI Robotics
#  See https://hebi.us/softwarelicense for license details
#
# -----------------------------------------------------------------------------
"""
This handles the bindings at the ctypes level. This is an internal API
and should not be used externally.
"""

from ctypes import (c_int, c_int32, c_int64, c_uint8, c_uint64, c_size_t,
                    c_float, c_double, c_char_p, c_void_p, POINTER, cdll, byref)

from os import environ
from os.path import dirname, join, realpath
from platform import machine, architecture
import re
import sys

from . import debug
debug.set_debug_mode('HEBI_DEBUG' in environ)
global _hebi_c_version


# -----------------------------------------------------------------------------
# Loading HEBI C API library
# -----------------------------------------------------------------------------


def _try_load_hebi_library(loc):
  try:
    lib = cdll.LoadLibrary(loc)
    debug.debug_log('Successfully loaded library at {0}'.format(loc))
    return lib, loc
  except:
    return None, None


def _load_hebi_lib_from_env():
  environ_val = environ.get('HEBI_C_LIB')
  if environ_val is not None:
    debug.debug_log(
      'Trying to load HEBI Core library from HEBI_C_LIB'
      ' environment variable ({0})'.format(environ_val))
    hebi_lib_obj, hebi_lib_loc = _try_load_hebi_library(environ_val)
    if hebi_lib_obj is not None:
      return hebi_lib_obj, hebi_lib_loc
    else:
      debug.warn_log(
        'The file or directory {0}'.format(environ_val) +\
        ' referenced by environment variable HEBI_C_LIB is not a'
        ' valid shared library')

  return None


def _load_hebi_lib_lnx(lib_base_path):
  cpu = machine()
  py_exec_arch = architecture()[0]
  lib_str = 'libhebi.so.{0}'.format(_hebi_c_version)

  if cpu == 'x86_64' and ('64' in py_exec_arch):
    # 64 bit x86 CPU with 64 bit python
    lib_path = join(lib_base_path, 'linux_x86_64', lib_str)

  elif ((re.match('i[3-6]86', cpu) is not None)
        or (cpu == 'x86_64') and ('32' in py_exec_arch)):
    # 64 OR 32 bit x86 CPU with 32 bit python (covers multilib Linux)
    lib_path = join(lib_base_path, 'linux_i686', lib_str)

  elif (re.match('arm.*', cpu) is not None) and ('32' in py_exec_arch):
    # 32 bit armhf with 32 bit python
    lib_path = join(lib_base_path, 'linux_armhf', lib_str)

  elif ((re.match('arm.*', cpu) is not None)
        or 'aarch64' in cpu and ('64' in py_exec_arch)):
    lib_path = join(lib_base_path, 'linux_aarch64', lib_str)
  else:
    raise RuntimeError('Unknown architecture {0}'.format(cpu))

  return _try_load_hebi_library(lib_path)


def _load_hebi_lib_osx(lib_base_path):
  lib_str = 'libhebi.{0}.dylib'.format(_hebi_c_version)
  lib_path = join(lib_base_path, 'osx_amd64', lib_str)
  return _try_load_hebi_library(lib_path)


def _load_hebi_lib_win(lib_base_path):
  cpu = machine()

  if cpu == 'AMD64':
    lib_path = join(lib_base_path, 'win_x64', 'hebi.dll')
  elif cpu == 'x86':
    lib_path = join(lib_base_path, 'win_x86', 'hebi.dll')
  elif cpu == 'ARM':
    # XXX Not yet supported :(
    # 32 bit ARM on Windows
    raise RuntimeError('ARM is not yet supported on Windows')
  elif cpu == 'ARM64':
    # XXX Not yet supported :(
    # 64 bit ARM on Windows
    raise RuntimeError('ARM64 is not yet supported on Windows')
  else:
    raise RuntimeError('Unknown architecture {0}'.format(cpu))

  return _try_load_hebi_library(lib_path)


def _load_hebi_lib_from_pkg():
  local_path = join(dirname(realpath(__file__)), '..')
  lib_base_path = join(local_path, 'lib')
  if sys.platform.startswith('linux'): # Python 2.x can return `linux2`
    return _load_hebi_lib_lnx(lib_base_path)
  elif sys.platform == 'darwin':
    return _load_hebi_lib_osx(lib_base_path)
  elif sys.platform == 'win32':
    return _load_hebi_lib_win(lib_base_path)
  raise RuntimeError('Unknown/Unsupported platform')


def _load_hebi_library():
# First check if environment variable "HEBI_C_LIB" is set.
# If it is, see if it is a valid library.
  hebi_lib_obj = _load_hebi_lib_from_env()

# Otherwise, load the binary for the current architecture
# provided by the `hebi-py` package
  if hebi_lib_obj is not None:
    return hebi_lib_obj
  return _load_hebi_lib_from_pkg()


# -----------------------------------------------------------------------------
# Finding HEBI Core API Functions from loaded shared library
# -----------------------------------------------------------------------------


class CTypeFuncDesc(object):
  """
  Structure which holds function signature info. For internal use.
  """
  def __init__(self, name, argtypes, restype):
    self._name = name
    self._argtypes = argtypes
    self._restype = restype

  @property
  def name(self):
    return self._name

  @property
  def argtypes(self):
    return self._argtypes

  @property
  def restype(self):
    return self._restype


def _init_lib_function(handle, desc):
  try:
    attr = getattr(handle, desc.name)
    attr.argtypes = desc.argtypes
    attr.restype = desc.restype
    # Set function as global variable of this module
    func = UnmanagedFunction(attr, desc.name)
    setattr(sys.modules[__name__], desc.name, func)
    debug.debug_log('Loaded C function {0}'.format(desc.name))
  except BaseException as err:
    debug.warn_log(
      'Could not initialize API function {0}'.format(desc.name))


def _create_func_table():
  c_size_t_p = POINTER(c_size_t)
  c_char_pp = POINTER(c_char_p)
  c_float_p = POINTER(c_float)
  c_double_p = POINTER(c_double)
  c_int32_p = POINTER(c_int32)
  c_int64_p = POINTER(c_int64)
  c_uint8_p = POINTER(c_uint8)
  c_uint64_p = POINTER(c_uint64)
  api_functions = [
    # -----------------------------------------------------------------------------
    # Lookup Functions
    # -----------------------------------------------------------------------------
    CTypeFuncDesc("hebiLookupCreate", [], c_void_p),
    CTypeFuncDesc("hebiLookupRelease", [c_void_p], None),
    CTypeFuncDesc("hebiCreateLookupEntryList", [c_void_p], c_void_p),
    CTypeFuncDesc("hebiLookupEntryListGetSize", [c_void_p], c_size_t),
    CTypeFuncDesc("hebiLookupEntryListGetName", [c_void_p, c_size_t, c_char_p, c_size_t_p], c_int),
    CTypeFuncDesc("hebiLookupEntryListGetFamily", [c_void_p, c_size_t, c_char_p, c_size_t_p], c_int),
    CTypeFuncDesc("hebiLookupEntryListGetMacAddress", [c_void_p, c_size_t, c_void_p], c_int),
    CTypeFuncDesc("hebiLookupEntryListRelease", [c_void_p], None),
    # -----------------------------------------------------------------------------
    # Group Functions
    # -----------------------------------------------------------------------------
    CTypeFuncDesc("hebiGroupCreateImitation", [c_size_t], c_void_p),
    CTypeFuncDesc("hebiGroupCreateFromMacs", [c_void_p, c_void_p, c_size_t, c_int32], c_void_p),
    CTypeFuncDesc("hebiGroupCreateFromNames", [c_void_p, c_char_pp, c_size_t, c_char_pp, c_size_t, c_int32], c_void_p),
    CTypeFuncDesc("hebiGroupCreateFromFamily", [c_void_p, c_char_p, c_int32], c_void_p),
    CTypeFuncDesc("hebiGroupCreateConnectedFromMac", [c_void_p, c_void_p, c_int32], c_void_p),
    CTypeFuncDesc("hebiGroupCreateConnectedFromName", [c_void_p, c_char_p, c_char_p, c_int32], c_void_p),
    CTypeFuncDesc("hebiGroupGetSize", [c_void_p], c_size_t),
    CTypeFuncDesc("hebiGroupSendCommandWithAcknowledgement", [c_void_p, c_void_p, c_int32], c_int),
    CTypeFuncDesc("hebiGroupSendCommand", [c_void_p, c_void_p], c_int),
    CTypeFuncDesc("hebiGroupSetCommandLifetime", [c_void_p, c_int32], c_int),
    CTypeFuncDesc("hebiGroupGetCommandLifetime", [c_void_p], c_int32),
    CTypeFuncDesc("hebiGroupSetFeedbackFrequencyHz", [c_void_p, c_float], c_int),
    CTypeFuncDesc("hebiGroupGetFeedbackFrequencyHz", [c_void_p], c_float),
    CTypeFuncDesc("hebiGroupRegisterFeedbackHandler", [c_void_p, c_void_p, c_void_p], c_int),
    CTypeFuncDesc("hebiGroupClearFeedbackHandlers", [c_void_p], None),
    CTypeFuncDesc("hebiGroupSendFeedbackRequest", [c_void_p], c_int),
    CTypeFuncDesc("hebiGroupGetNextFeedback", [c_void_p, c_void_p, c_int32], c_int),
    CTypeFuncDesc("hebiGroupRequestInfo", [c_void_p, c_void_p, c_int32], c_int),
    CTypeFuncDesc("hebiGroupStartLog", [c_void_p, c_char_p, c_char_p, c_void_p], c_int),
    CTypeFuncDesc("hebiGroupStopLog", [c_void_p], c_void_p),
    CTypeFuncDesc("hebiGroupRelease", [c_void_p], None),
    # -----------------------------------------------------------------------------
    # Group Command Functions
    # -----------------------------------------------------------------------------
    CTypeFuncDesc("hebiGroupCommandCreate", [c_size_t], c_void_p),
    CTypeFuncDesc("hebiGroupCommandGetSize", [c_void_p], c_size_t),
    CTypeFuncDesc("hebiGroupCommandReadGains", [c_void_p, c_char_p], c_int),
    CTypeFuncDesc("hebiGroupCommandWriteGains", [c_void_p, c_char_p], c_int),
    CTypeFuncDesc("hebiGroupCommandGetModuleCommand", [c_void_p, c_size_t], c_void_p),
    CTypeFuncDesc("hebiGroupCommandClear", [c_void_p], None),
    CTypeFuncDesc("hebiGroupCommandRelease", [c_void_p], None),
    # -----------------------------------------------------------------------------
    # Group Feedback Functions
    # -----------------------------------------------------------------------------
    CTypeFuncDesc("hebiGroupFeedbackCreate", [c_size_t], c_void_p),
    CTypeFuncDesc("hebiGroupFeedbackGetSize", [c_void_p], c_size_t),
    CTypeFuncDesc("hebiGroupFeedbackGetModuleFeedback", [c_void_p, c_size_t], c_void_p),
    CTypeFuncDesc("hebiGroupFeedbackCopy", [c_void_p, c_void_p], c_int),
    CTypeFuncDesc("hebiGroupFeedbackClear", [c_void_p], None),
    CTypeFuncDesc("hebiGroupFeedbackRelease", [c_void_p], None),
    # -----------------------------------------------------------------------------
    # Group Info Functions
    # -----------------------------------------------------------------------------
    CTypeFuncDesc("hebiGroupInfoCreate", [c_size_t], c_void_p),
    CTypeFuncDesc("hebiGroupInfoGetSize", [c_void_p], c_size_t),
    CTypeFuncDesc("hebiGroupInfoWriteGains", [c_void_p, c_char_p], c_int),
    CTypeFuncDesc("hebiGroupInfoGetModuleInfo", [c_void_p, c_size_t], c_void_p),
    CTypeFuncDesc("hebiGroupInfoRelease", [c_void_p], None),
    # -----------------------------------------------------------------------------
    # Command Field Functions
    # -----------------------------------------------------------------------------
    CTypeFuncDesc("hebiCommandGetFloat", [c_void_p, c_int, c_float_p], c_int),
    CTypeFuncDesc("hebiCommandSetFloat", [c_void_p, c_int, c_float_p], None),
    CTypeFuncDesc("hebiCommandGetHighResAngle", [c_void_p, c_int, c_int64_p, c_float_p], c_int),
    CTypeFuncDesc("hebiCommandSetHighResAngle", [c_void_p, c_int, c_int64_p, c_float_p], None),
    CTypeFuncDesc("hebiCommandGetNumberedFloat", [c_void_p, c_int, c_size_t, c_float_p], c_int),
    CTypeFuncDesc("hebiCommandSetNumberedFloat", [c_void_p, c_int, c_size_t, c_float_p], None),
    CTypeFuncDesc("hebiCommandGetBool", [c_void_p, c_int, c_int32_p], c_int),
    CTypeFuncDesc("hebiCommandSetBool", [c_void_p, c_int, c_int32_p], None),
    CTypeFuncDesc("hebiCommandGetString", [c_void_p, c_int, c_char_p, c_size_t_p], c_int),
    CTypeFuncDesc("hebiCommandSetString", [c_void_p, c_int, c_char_p, c_size_t_p], None),
    CTypeFuncDesc("hebiCommandGetFlag", [c_void_p, c_int], c_int32),
    CTypeFuncDesc("hebiCommandSetFlag", [c_void_p, c_int, c_int32], None),
    CTypeFuncDesc("hebiCommandGetEnum", [c_void_p, c_int, c_int32_p], c_int),
    CTypeFuncDesc("hebiCommandSetEnum", [c_void_p, c_int, c_int32_p], None),
    CTypeFuncDesc("hebiCommandGetIoPinInt", [c_void_p, c_int, c_size_t, c_int64_p], c_int),
    CTypeFuncDesc("hebiCommandGetIoPinFloat", [c_void_p, c_int, c_size_t, c_float_p], c_int),
    CTypeFuncDesc("hebiCommandSetIoPinInt", [c_void_p, c_int, c_size_t, c_int64_p], None),
    CTypeFuncDesc("hebiCommandSetIoPinFloat", [c_void_p, c_int, c_size_t, c_float_p], None),
    CTypeFuncDesc("hebiCommandGetLedColor", [c_void_p, c_int, c_uint8_p, c_uint8_p, c_uint8_p], c_int),
    CTypeFuncDesc("hebiCommandHasLedModuleControl", [c_void_p, c_int], c_int32),
    CTypeFuncDesc("hebiCommandSetLedOverrideColor", [c_void_p, c_int, c_uint8, c_uint8, c_uint8], None),
    CTypeFuncDesc("hebiCommandSetLedModuleControl", [c_void_p, c_int], None),
    CTypeFuncDesc("hebiCommandClearLed", [c_void_p, c_int], None),
    # -----------------------------------------------------------------------------
    # Feedback Field Functions
    # -----------------------------------------------------------------------------
    CTypeFuncDesc("hebiFeedbackGetFloat", [c_void_p, c_int, c_float_p], c_int),
    CTypeFuncDesc("hebiFeedbackGetHighResAngle", [c_void_p, c_int, c_int64_p, c_float_p], c_int),
    CTypeFuncDesc("hebiFeedbackGetUInt64", [c_void_p, c_int, c_uint64_p], c_int),
    CTypeFuncDesc("hebiFeedbackGetNumberedFloat", [c_void_p, c_int, c_size_t, c_float_p], c_int),
    CTypeFuncDesc("hebiFeedbackGetEnum", [c_void_p, c_int, c_int32_p], c_int),
    CTypeFuncDesc("hebiFeedbackGetVector3f", [c_void_p, c_int, c_void_p], c_int),
    CTypeFuncDesc("hebiFeedbackGetQuaternionf", [c_void_p, c_int, c_void_p], c_int),
    CTypeFuncDesc("hebiFeedbackGetIoPinInt", [c_void_p, c_int, c_size_t, c_int64_p], c_int),
    CTypeFuncDesc("hebiFeedbackGetIoPinFloat", [c_void_p, c_int, c_size_t, c_float_p], c_int),
    CTypeFuncDesc("hebiFeedbackGetLedColor", [c_void_p, c_int, c_uint8_p, c_uint8_p, c_uint8_p], c_int),
    # -----------------------------------------------------------------------------
    # Info Field Functions
    # -----------------------------------------------------------------------------
    CTypeFuncDesc("hebiInfoGetFloat", [c_void_p, c_int, c_float_p], c_int),
    CTypeFuncDesc("hebiInfoGetHighResAngle", [c_void_p, c_int, c_int64_p, c_float_p], c_int),
    CTypeFuncDesc("hebiInfoGetBool", [c_void_p, c_int, c_int32_p], c_int),
    CTypeFuncDesc("hebiInfoGetString", [c_void_p, c_int, c_char_p, c_size_t_p], c_int),
    CTypeFuncDesc("hebiInfoGetFlag", [c_void_p, c_int], c_int32),
    CTypeFuncDesc("hebiInfoGetEnum", [c_void_p, c_int, c_int32_p], c_int),
    CTypeFuncDesc("hebiInfoGetLedColor", [c_void_p, c_int, c_uint8_p, c_uint8_p, c_uint8_p], c_int),
    # -----------------------------------------------------------------------------
    # Robot Model Functions
    # -----------------------------------------------------------------------------
    CTypeFuncDesc("hebiRobotModelElementCreateJoint", [c_int], c_void_p),
    CTypeFuncDesc("hebiRobotModelElementCreateRigidBody", [c_double_p, c_double_p, c_double, c_size_t, c_double_p],
                  c_void_p),
    CTypeFuncDesc("hebiRobotModelElementCreateActuator", [c_int], c_void_p),
    CTypeFuncDesc("hebiRobotModelElementCreateBracket", [c_int], c_void_p),
    CTypeFuncDesc("hebiRobotModelElementCreateLink", [c_int, c_double, c_double], c_void_p),
    CTypeFuncDesc("hebiRobotModelElementRelease", [c_void_p], None),
    CTypeFuncDesc("hebiRobotModelCreate", [], c_void_p),
    CTypeFuncDesc("hebiRobotModelSetBaseFrame", [c_void_p, c_double_p], c_int),
    CTypeFuncDesc("hebiRobotModelGetBaseFrame", [c_void_p, c_double_p], c_int),
    CTypeFuncDesc("hebiRobotModelGetNumberOfFrames", [c_void_p, c_int], c_size_t),
    CTypeFuncDesc("hebiRobotModelGetNumberOfDoFs", [c_void_p], c_size_t),
    CTypeFuncDesc("hebiRobotModelAdd", [c_void_p, c_void_p, c_size_t, c_void_p, c_int32], c_int),
    CTypeFuncDesc("hebiRobotModelGetForwardKinematics", [c_void_p, c_int, c_double_p, c_double_p], c_int),
    CTypeFuncDesc("hebiRobotModelGetJacobians", [c_void_p, c_int, c_double_p, c_double_p], c_int),
    CTypeFuncDesc("hebiRobotModelGetMasses", [c_void_p, c_double_p], c_int),
    CTypeFuncDesc("hebiRobotModelRelease", [c_void_p], None),
    # -----------------------------------------------------------------------------
    # Inverse Kinematics Functions
    # -----------------------------------------------------------------------------
    CTypeFuncDesc("hebiIKCreate", [], c_void_p),
    CTypeFuncDesc("hebiIKAddObjectiveEndEffectorPosition", [c_void_p, c_float, c_size_t, c_double, c_double, c_double],
                  c_int),
    CTypeFuncDesc("hebiIKAddObjectiveEndEffectorSO3", [c_void_p, c_double, c_size_t, c_double_p], c_int),
    CTypeFuncDesc("hebiIKAddObjectiveEndEffectorTipAxis", [c_void_p, c_double, c_size_t, c_double, c_double, c_double],
                  c_int),
    CTypeFuncDesc("hebiIKAddConstraintJointAngles", [c_void_p, c_double, c_size_t, c_double_p, c_double_p], c_int),
    CTypeFuncDesc("hebiIKAddObjectiveCustom", [c_void_p, c_double, c_size_t, c_void_p, c_void_p], c_int),
    CTypeFuncDesc("hebiIKClearAll", [c_void_p], None),
    CTypeFuncDesc("hebiIKSolve", [c_void_p, c_void_p, c_double_p, c_double_p, c_void_p], c_int),
    CTypeFuncDesc("hebiIKRelease", [c_void_p], None),
    # -----------------------------------------------------------------------------
    # Trajectory Functions
    # -----------------------------------------------------------------------------
    CTypeFuncDesc("hebiTrajectoryCreateUnconstrainedQp", [c_size_t, c_double_p, c_double_p, c_double_p, c_double_p],
                  c_void_p),
    CTypeFuncDesc("hebiTrajectoryRelease", [c_void_p], None),
    CTypeFuncDesc("hebiTrajectoryGetDuration", [c_void_p], c_double),
    CTypeFuncDesc("hebiTrajectoryGetState", [c_void_p, c_double, c_double_p, c_double_p, c_double_p], c_int),
    # -----------------------------------------------------------------------------
    # Log File Functions
    # -----------------------------------------------------------------------------
    CTypeFuncDesc("hebiLogFileRelease", [c_void_p], None),
    CTypeFuncDesc("hebiLogFileGetFileName", [c_void_p, c_char_p, c_size_t_p], c_int),
    CTypeFuncDesc("hebiLogFileOpen", [c_char_p], c_void_p),
    CTypeFuncDesc("hebiLogFileGetNumberOfModules", [c_void_p], c_size_t),
    CTypeFuncDesc("hebiLogFileGetNextFeedback", [c_void_p, c_void_p], c_int),
    # -----------------------------------------------------------------------------
    # String Functions
    # -----------------------------------------------------------------------------
    CTypeFuncDesc("hebiStringGetString", [c_void_p, c_char_p, c_size_t_p], c_int),
    CTypeFuncDesc("hebiStringRelease", [c_void_p], None),
    # -----------------------------------------------------------------------------
    # Miscellaneous Functions
    # -----------------------------------------------------------------------------
    CTypeFuncDesc("hebiCleanup", [], None),
  ]
  return api_functions


_c_api_functions = _create_func_table()

def _load_hebi_functions(handle, api_functions):
  for api_function in api_functions:
    _init_lib_function(handle, api_function)


def _init_hebi_library():
  native_lib, native_loc = _load_hebi_library()
  if native_lib is None:
    debug.warn_log('Could not load HEBI Core library')
    raise RuntimeError('HEBI Core library not found')

  _load_hebi_functions(native_lib, _c_api_functions)
  return native_lib, native_loc


# -----------------------------------------------------------------------------
# Profiler Code
# -----------------------------------------------------------------------------


import sys
if sys.version_info[0] == 3 and sys.version_info[1] >= 3:
  from time import perf_counter as _get_time
else:
  from time import time as _get_time
from time import strftime


import numpy as np
import threading
class _HebiProfilerTLS(threading.local):
  def __init_dict(self):
    for entry in _c_api_functions:
      self.func_stats[entry.name] = list()

  def __init__(self):
    super(_HebiProfilerTLS, self).__init__()
    self.func_name = None
    self.start_time = None
    self.func_stats = dict()
    self.__init_dict()


class _SimpleHEBIProfiler(object):
  def __init__(self):
    self._tls = _HebiProfilerTLS()

  def enter(self, func_name):
    self._tls.func_name = func_name
    self._tls.start_time = _get_time()

  def exit(self):
    self._tls.func_stats[self._tls.func_name].append(_get_time()-self._tls.start_time)

  def _write_entry(self, f, func_name):
    entries = self._tls.func_stats[func_name]
    if len(entries) == 0:
      return
    entries = np.array(entries)
    min_val = np.amin(entries)
    max_val = np.amax(entries)
    mean = np.mean(entries)
    stddev = np.std(entries)
    count = entries.size
    pct_90 = np.percentile(entries, 90)
    pct_95 = np.percentile(entries, 95)
    pct_99 = np.percentile(entries, 99)
    cumulative = np.sum(entries)
    f.write('{0},{1},{2},{3},{4},{5},{6},{7},{8},{9}\n'.format(func_name, count,
                                                               cumulative, mean,
                                                               min_val, max_val,
                                                               stddev, pct_90,
                                                               pct_95, pct_99))

  def dump_stats(self, path=None):
    if path is None:
      thd = threading.current_thread()
      path = '{0}_{1}-{2}_c_profile.csv'.format(strftime('%m_%d_%y_%H-%M-%S'),
                                                thd.name, thd.ident)

    with open(path, 'w') as f:
      f.write('function,count,cumulative,avg,min,max,stddev,90pct,95pct,99pct\n')
      for func_name in self._tls.func_stats.keys():
        self._write_entry(f, func_name)


_C_API_profiler = _SimpleHEBIProfiler()


def _enter_c_func(func_name):
  _C_API_profiler.enter(func_name)


def _exit_c_func():
  _C_API_profiler.exit()


def _dump_c_api_stats(path=None):
  _C_API_profiler.dump_stats(path)


# -----------------------------------------------------------------------------
# C API Wrapper
# -----------------------------------------------------------------------------


class UnmanagedFunction(object):
  """
  TODO: Document
  """

  __status_code_map = {
    0 : 'StatusSuccess',
    1 : 'StatusInvalidArgument',
    2 : 'StatusBufferTooSmall',
    3 : 'StatusValueNotSet',
    4 : 'StatusFailure',
    5 : 'StatusArgumentOutOfRange' }

  def __init__(self, func, func_name):
    self._func = func
    self._func_name = func_name

    if func.restype == c_int:
      def dbg_callback(fmtd_call, *args, **kwargs):
        res = self._func(*args, **kwargs)
        res_str = UnmanagedFunction.__status_code_map.get(res, '__Unknown__')
        debug.debug_log('{0} ==> {1}'.format(fmtd_call, res_str))
        return res

    elif func.restype is None:
      def dbg_callback(fmtd_call, *args, **kwargs):
        self._func(*args, **kwargs)
        debug.debug_log('{0} ==> None'.format(fmtd_call))
        return None

    else:
      def dbg_callback(fmtd_call, *args, **kwargs):
        res = self._func(*args, **kwargs)
        debug.debug_log('{0} ==> {1}'.format(fmtd_call, res))
        return res

    self._dbg_callback = dbg_callback
    self._call_impl = None
    self.update_call_function()

  def __repr__(self):
    return "Unmanaged Function '{0}'".format(self._func_name) +\
            " (ctype: {0})".format(repr(self._func))

  def __str__(self):
    return self._func_name

  def __call__(self, *args, **kwargs):
    return self._call_impl(*args, **kwargs)

  def update_call_function(self):
    """
    Called when the debug mode is changed
    :return:
    """
    import os
    if 'HEBI_PROFILE' in os.environ:
      if debug.debug_mode():
        def call_impl(*args, **kwargs):
          fmtd_call = '{0}{1}'.format(self._func_name, args)
          _enter_c_func(self._func_name)
          ret = self._dbg_callback(fmtd_call, *args, **kwargs)
          _exit_c_func()
          return ret
        self._call_impl = call_impl
      else:
        def call_impl(*args, **kwargs):
          _enter_c_func(self._func_name)
          ret = self._func(*args, **kwargs)
          _exit_c_func()
          return ret
        self._call_impl = call_impl
    else:
      if debug.debug_mode():
        def call_impl(*args, **kwargs):
          fmtd_call = '{0}{1}'.format(self._func_name, args)
          return self._dbg_callback(fmtd_call, *args, **kwargs)
        self._call_impl = call_impl
      else:
        self._call_impl = self._func


class UnmanagedObject(object):
  """
  Base class for an object created by the HEBI C API.
  """

  def __init__(self, internal, on_delete=None):
    self._internal = internal
    self._on_delete = on_delete

  @property
  def _as_parameter_(self):
    return self._internal

  def __del__(self):
    if self._on_delete and self._internal:
      self._on_delete(self)


class UnmanagedSharedObject(UnmanagedObject):
  """
  Base class for an object from the HEBI C API which requires
  reference counting.
  """

  def __init__(self, internal, on_delete=None):
    super(UnmanagedSharedObject, self).__init__(internal, on_delete)
    from .utils import AtomicCounter
    self._refcount = AtomicCounter()

  def __del__(self):
    self._refcount.decrement()
    if self._refcount.count < 1:
      super(UnmanagedSharedObject, self).__del__()

  def add_ref(self):
    """
    Called when another new object is about to share of this object
    :return: A copy of this object
    """
    ret = UnmanagedSharedObject(None)
    ret._internal = self._internal
    ret._on_delete = self._on_delete
    ret._refcount = self._refcount
    self._refcount.increment()

    # TODO: Find way where we don't have to do this hackiness
    return ret


class HEBI_Library_Wrapper(object):
  """
  Loads the C API functions. Do not use.
  """

  _c_min_major = 1
  """ Required minimum major version for C library """
  _c_min_minor = 3
  """ Required minimum minor version for C library """
  _c_min_patch = 0
  """ Required minimum patch version for C library """

  def __on_init(self):
    if hasattr(self.api, 'hebiGetLibraryVersion'):
      """ Get C API version, if the function exists """

      major_version = c_int32(0)
      minor_version = c_int32(0)
      patch_version = c_int32(0)

      c_int32_p = POINTER(c_int32)
      attr = self.api.hebiGetLibraryVersion
      attr.argtypes = [c_int32_p, c_int32_p, c_int32_p]
      attr.restype = c_int

      self.api.hebiGetLibraryVersion(byref(major_version),
                                     byref(minor_version),
                                     byref(patch_version))

      req_str = '{0}.{1}.{2}'.format(self._c_min_major,
                                     self._c_min_minor,
                                     self._c_min_patch)
      cur_str = '{0}.{1}.{2}'.format(major_version.value,
                                     minor_version.value,
                                     patch_version.value)
      if cur_str < req_str:
        print('Warning: loaded C library may be incompatible, as it is'
              ' an outdated library. Loaded library version is '
              '{0}, required minimum is {1}'.format(cur_str, req_str))
      debug.debug_log('hebiGetLibraryVersion() ==> {0}'.format(cur_str))

  def __init__(self, tuple):
    api = tuple[0]
    location = tuple[1]
    self.api = api
    self.__location = location
    self.__on_init()

  def __del__(self):
    if self.api:
      self.api.hebiCleanup()

  @property
  def location(self):
    return self.__location


# -----------------------------------------------------------------------------
# Make the C API functions available at module scope
# -----------------------------------------------------------------------------


class NotImplementedCFunction(object):
  """
  Initial class used for HEBI C API functions. This way, we catch
  any attempted calls to the C API that are for whatever reason missing.
  """

  def __init__(self, func_name):
    self._func_name = func_name

  def __call__(self, *args, **kwargs):
    print('Error: C API function {0} not found'.format(self._func_name) +
      ' in library located at {0}'.format(_handle.location) +
      ' - you probably have an old or corrupted'
      ' HEBI C library.')
    raise NotImplementedError


# Avoid typing all of these characters for below
_T = NotImplementedCFunction
hebiLookupCreate = _T('hebiLookupCreate')
hebiLookupRelease = _T('hebiLookupRelease')
hebiCreateLookupEntryList = _T('hebiCreateLookupEntryList')
hebiLookupEntryListGetSize = _T('hebiLookupEntryListGetSize')
hebiLookupEntryListGetName = _T('hebiLookupEntryListGetName')
hebiLookupEntryListGetFamily = _T('hebiLookupEntryListGetFamily')
hebiLookupEntryListGetMacAddress = _T('hebiLookupEntryListGetMacAddress')
hebiLookupEntryListRelease = _T('hebiLookupEntryListRelease')
hebiGroupCreateImitation = _T('hebiGroupCreateImitation')
hebiGroupCreateFromMacs = _T('hebiGroupCreateFromMacs')
hebiGroupCreateFromNames = _T('hebiGroupCreateFromNames')
hebiGroupCreateFromFamily = _T('hebiGroupCreateFromFamily')
hebiGroupCreateConnectedFromMac = _T('hebiGroupCreateConnectedFromMac')
hebiGroupCreateConnectedFromName = _T('hebiGroupCreateConnectedFromName')
hebiGroupGetSize = _T('hebiGroupGetSize')
hebiGroupSendCommandWithAcknowledgement = _T('hebiGroupSendCommandWithAcknowledgement')
hebiGroupSendCommand = _T('hebiGroupSendCommand')
hebiGroupSetCommandLifetime = _T('hebiGroupSetCommandLifetime')
hebiGroupGetCommandLifetime = _T('hebiGroupGetCommandLifetime')
hebiGroupSetFeedbackFrequencyHz = _T('hebiGroupSetFeedbackFrequencyHz')
hebiGroupGetFeedbackFrequencyHz = _T('hebiGroupGetFeedbackFrequencyHz')
hebiGroupRegisterFeedbackHandler = _T('hebiGroupRegisterFeedbackHandler')
hebiGroupClearFeedbackHandlers = _T('hebiGroupClearFeedbackHandlers')
hebiGroupSendFeedbackRequest = _T('hebiGroupSendFeedbackRequest')
hebiGroupGetNextFeedback = _T('hebiGroupGetNextFeedback')
hebiGroupRequestInfo = _T('hebiGroupRequestInfo')
hebiGroupStartLog = _T('hebiGroupStartLog')
hebiGroupStopLog = _T('hebiGroupStopLog')
hebiGroupRelease = _T('hebiGroupRelease')
hebiGroupCommandCreate = _T('hebiGroupCommandCreate')
hebiGroupCommandGetSize = _T('hebiGroupCommandGetSize')
hebiGroupCommandReadGains = _T('hebiGroupCommandReadGains')
hebiGroupCommandWriteGains = _T('hebiGroupCommandWriteGains')
hebiGroupCommandGetModuleCommand = _T('hebiGroupCommandGetModuleCommand')
hebiGroupCommandClear = _T('hebiGroupCommandClear')
hebiGroupCommandRelease = _T('hebiGroupCommandRelease')
hebiGroupFeedbackCreate = _T('hebiGroupFeedbackCreate')
hebiGroupFeedbackGetSize = _T('hebiGroupFeedbackGetSize')
hebiGroupFeedbackGetModuleFeedback = _T('hebiGroupFeedbackGetModuleFeedback')
hebiGroupFeedbackCopy = _T('hebiGroupFeedbackCopy')
hebiGroupFeedbackClear = _T('hebiGroupFeedbackClear')
hebiGroupFeedbackRelease = _T('hebiGroupFeedbackRelease')
hebiGroupInfoCreate = _T('hebiGroupInfoCreate')
hebiGroupInfoGetSize = _T('hebiGroupInfoGetSize')
hebiGroupInfoWriteGains = _T('hebiGroupInfoWriteGains')
hebiGroupInfoGetModuleInfo = _T('hebiGroupInfoGetModuleInfo')
hebiGroupInfoRelease = _T('hebiGroupInfoRelease')
hebiCommandGetFloat = _T('hebiCommandGetFloat')
hebiCommandSetFloat = _T('hebiCommandSetFloat')
hebiCommandGetHighResAngle = _T('hebiCommandGetHighResAngle')
hebiCommandSetHighResAngle = _T('hebiCommandSetHighResAngle')
hebiCommandGetNumberedFloat = _T('hebiCommandGetNumberedFloat')
hebiCommandSetNumberedFloat = _T('hebiCommandSetNumberedFloat')
hebiCommandGetBool = _T('hebiCommandGetBool')
hebiCommandSetBool = _T('hebiCommandSetBool')
hebiCommandGetString = _T('hebiCommandGetString')
hebiCommandSetString = _T('hebiCommandSetString')
hebiCommandGetFlag = _T('hebiCommandGetFlag')
hebiCommandSetFlag = _T('hebiCommandSetFlag')
hebiCommandGetEnum = _T('hebiCommandGetEnum')
hebiCommandSetEnum = _T('hebiCommandSetEnum')
hebiCommandGetIoPinInt = _T('hebiCommandGetIoPinInt')
hebiCommandGetIoPinFloat = _T('hebiCommandGetIoPinFloat')
hebiCommandSetIoPinInt = _T('hebiCommandSetIoPinInt')
hebiCommandSetIoPinFloat = _T('hebiCommandSetIoPinFloat')
hebiCommandGetLedColor = _T('hebiCommandGetLedColor')
hebiCommandHasLedModuleControl = _T('hebiCommandHasLedModuleControl')
hebiCommandSetLedOverrideColor = _T('hebiCommandSetLedOverrideColor')
hebiCommandSetLedModuleControl = _T('hebiCommandSetLedModuleControl')
hebiCommandClearLed = _T('hebiCommandClearLed')
hebiFeedbackGetFloat = _T('hebiFeedbackGetFloat')
hebiFeedbackGetHighResAngle = _T('hebiFeedbackGetHighResAngle')
hebiFeedbackGetUInt64 = _T('hebiFeedbackGetUInt64')
hebiFeedbackGetNumberedFloat = _T('hebiFeedbackGetNumberedFloat')
hebiFeedbackGetEnum = _T('hebiFeedbackGetEnum')
hebiFeedbackGetVector3f = _T('hebiFeedbackGetVector3f')
hebiFeedbackGetQuaternionf = _T('hebiFeedbackGetQuaternionf')
hebiFeedbackGetIoPinInt = _T('hebiFeedbackGetIoPinInt')
hebiFeedbackGetIoPinFloat = _T('hebiFeedbackGetIoPinFloat')
hebiFeedbackGetLedColor = _T('hebiFeedbackGetLedColor')
hebiInfoGetFloat = _T('hebiInfoGetFloat')
hebiInfoGetHighResAngle = _T('hebiInfoGetHighResAngle')
hebiInfoGetBool = _T('hebiInfoGetBool')
hebiInfoGetString = _T('hebiInfoGetString')
hebiInfoGetFlag = _T('hebiInfoGetFlag')
hebiInfoGetEnum = _T('hebiInfoGetEnum')
hebiInfoGetLedColor = _T('hebiInfoGetLedColor')
hebiRobotModelElementCreateJoint = _T('hebiRobotModelElementCreateJoint')
hebiRobotModelElementCreateRigidBody = _T('hebiRobotModelElementCreateRigidBody')
hebiRobotModelElementCreateActuator = _T('hebiRobotModelElementCreateActuator')
hebiRobotModelElementCreateBracket = _T('hebiRobotModelElementCreateBracket')
hebiRobotModelElementCreateLink = _T('hebiRobotModelElementCreateLink')
hebiRobotModelElementRelease = _T('hebiRobotModelElementRelease')
hebiRobotModelCreate = _T('hebiRobotModelCreate')
hebiRobotModelSetBaseFrame = _T('hebiRobotModelSetBaseFrame')
hebiRobotModelGetBaseFrame = _T('hebiRobotModelGetBaseFrame')
hebiRobotModelGetNumberOfFrames = _T('hebiRobotModelGetNumberOfFrames')
hebiRobotModelGetNumberOfDoFs = _T('hebiRobotModelGetNumberOfDoFs')
hebiRobotModelAdd = _T('hebiRobotModelAdd')
hebiRobotModelGetForwardKinematics = _T('hebiRobotModelGetForwardKinematics')
hebiRobotModelGetJacobians = _T('hebiRobotModelGetJacobians')
hebiRobotModelGetMasses = _T('hebiRobotModelGetMasses')
hebiRobotModelRelease = _T('hebiRobotModelRelease')
hebiIKCreate = _T('hebiIKCreate')
hebiIKAddObjectiveEndEffectorPosition = _T('hebiIKAddObjectiveEndEffectorPosition')
hebiIKAddObjectiveEndEffectorSO3 = _T('hebiIKAddObjectiveEndEffectorSO3')
hebiIKAddObjectiveEndEffectorTipAxis = _T('hebiIKAddObjectiveEndEffectorTipAxis')
hebiIKAddConstraintJointAngles = _T('hebiIKAddConstraintJointAngles')
hebiIKAddObjectiveCustom = _T('hebiIKAddObjectiveCustom')
hebiIKClearAll = _T('hebiIKClearAll')
hebiIKSolve = _T('hebiIKSolve')
hebiIKRelease = _T('hebiIKRelease')
hebiTrajectoryCreateUnconstrainedQp = _T('hebiTrajectoryCreateUnconstrainedQp')
hebiTrajectoryRelease = _T('hebiTrajectoryRelease')
hebiTrajectoryGetDuration = _T('hebiTrajectoryGetDuration')
hebiTrajectoryGetState = _T('hebiTrajectoryGetState')
hebiLogFileRelease = _T('hebiLogFileRelease')
hebiLogFileGetFileName = _T('hebiLogFileGetFileName')
hebiLogFileOpen = _T('hebiLogFileOpen')
hebiLogFileGetNumberOfModules = _T('hebiLogFileGetNumberOfModules')
hebiLogFileGetNextFeedback = _T('hebiLogFileGetNextFeedback')
hebiStringGetString = _T('hebiStringGetString')
hebiStringRelease = _T('hebiStringRelease')
hebiCleanup = _T('hebiCleanup')


# -----------------------------------------------------------------------------
# Make the C API Enum values available at module scope
# -----------------------------------------------------------------------------


class EnumTraits(object):
  """
  TODO: Document
  """

  def __init__(self, value, name):
    self._value = value
    self._name = name
    self._as_parameter_ = value

  @property
  def value(self):
    return self._value

  @property
  def name(self):
    return self._name

  def __int__(self):
    return self._value

  def __hash__(self):
    return self._value

  def __eq__(self, value):
    if type(value) is int:
      return value == self._value
    elif isinstance(value, EnumTraits):
      return (value._name == self._name) and (value._value == self._value)
    elif type(value) is str:
      return value == self._name
    else:
      return value == self._value

  def __ne__(self, value):
    if type(value) is int:
      return value != self._value
    elif isinstance(value, EnumTraits):
      return (value._name != self._name) and (value._value != self._value)
    elif type(value) is str:
      return value != self._name
    else:
      return value != self._value

  def __str__(self):
    return self._name

  def __repr__(self):
    return '{0} ({1})'.format(self._name, self._value)


class MessageEnumTraits(EnumTraits):
  """
  TODO: Document
  """

  def __init__(self, value, name,
               allow_broadcast=True,
               not_bcastable_reason='',
               yields_dict=None):
    super(MessageEnumTraits, self).__init__(value, name)
    self.__allow_broadcast = allow_broadcast
    self.__not_broadcastable_reason = not_bcastable_reason
    self.__products=yields_dict

    if yields_dict != None:
      substrate = dict()
      for key in yields_dict.keys():
        value = yields_dict[key].lower()
        substrate[value] = key
      self.__substrates = substrate
    else:
      self.__substrates = None

  @property
  def allow_broadcast(self):
    """
    Determines whether the given enum has the ability to broadcast the
    same value to all modules in a group
    """
    return self.__allow_broadcast

  @property
  def substrates(self):
    return self.__substrates

  @property
  def products(self):
    return self.__products

  @property
  def not_broadcastable_reason(self):
    if self.allow_broadcast:
      return ''
    return self.__not_broadcastable_reason

  def __repr__(self):
    if self.__allow_broadcast:
      return '{0} ({1}), broadcastable'.format(self._name, self._value)
    return '{0} ({1}), not broadcastable '.format(self._name, self._value) +\
           '({0})'.format(self.__not_broadcastable_reason)


# Status Codes
StatusSuccess = EnumTraits(0, 'StatusSuccess')
StatusInvalidArgument = EnumTraits(1, 'StatusInvalidArgument')
StatusBufferTooSmall = EnumTraits(2, 'StatusBufferTooSmall')
StatusValueNotSet = EnumTraits(3, 'StatusValueNotSet')
StatusFailure = EnumTraits(4, 'StatusFailure')
StatusArgumentOutOfRange = EnumTraits(5, 'StatusArgumentOutOfRange')

# Frame Types
FrameTypeCenterOfMass = EnumTraits(0, 'FrameTypeCenterOfMass')
FrameTypeOutput = EnumTraits(1, 'FrameTypeOutput')
FrameTypeEndEffector = EnumTraits(2, 'FrameTypeEndEffector')

# Types of motion allowed by joints
JointTypeRotationX = EnumTraits(0, 'JointTypeRotationX')
JointTypeRotationY = EnumTraits(1, 'JointTypeRotationY')
JointTypeRotationZ = EnumTraits(2, 'JointTypeRotationZ')
JointTypeTranslationX = EnumTraits(3, 'JointTypeTranslationX')
JointTypeTranslationY = EnumTraits(4, 'JointTypeTranslationY')
JointTypeTranslationZ = EnumTraits(5, 'JointTypeTranslationZ')

# Actuator Types
ActuatorTypeX5_1 = EnumTraits(0, 'ActuatorTypeX5_1')
ActuatorTypeX5_4 = EnumTraits(1, 'ActuatorTypeX5_4')
ActuatorTypeX5_9 = EnumTraits(2, 'ActuatorTypeX5_9')
ActuatorTypeX8_3 = EnumTraits(3, 'ActuatorTypeX8_3')
ActuatorTypeX8_9 = EnumTraits(4, 'ActuatorTypeX8_9')
ActuatorTypeX8_16 = EnumTraits(5, 'ActuatorTypeX8_16')

# Link Types
LinkTypeX5 = EnumTraits(0, 'LinkTypeX5')

# Bracket Types
BracketTypeX5LightLeft = EnumTraits(0, 'BracketTypeX5LightLeft')
BracketTypeX5LightRight = EnumTraits(1, 'BracketTypeX5LightRight')
BracketTypeX5HeavyLeftInside = EnumTraits(2, 'BracketTypeX5HeavyLeftInside')
BracketTypeX5HeavyLeftOutside = EnumTraits(3, 'BracketTypeX5HeavyLeftOutside')
BracketTypeX5HeavyRightInside = EnumTraits(4, 'BracketTypeX5HeavyRightInside')
BracketTypeX5HeavyRightOutside = EnumTraits(5, 'BracketTypeX5HeavyRightOutside')

# CommandFloatField
CommandFloatVelocity = MessageEnumTraits(0, 'CommandFloatVelocity')
CommandFloatEffort = MessageEnumTraits(1, 'CommandFloatEffort')
CommandFloatPositionKp = MessageEnumTraits(2, 'CommandFloatPositionKp')
CommandFloatPositionKi = MessageEnumTraits(3, 'CommandFloatPositionKi')
CommandFloatPositionKd = MessageEnumTraits(4, 'CommandFloatPositionKd')
CommandFloatPositionFeedForward = MessageEnumTraits(5, 'CommandFloatPositionFeedForward')
CommandFloatPositionDeadZone = MessageEnumTraits(6, 'CommandFloatPositionDeadZone')
CommandFloatPositionIClamp = MessageEnumTraits(7, 'CommandFloatPositionIClamp')
CommandFloatPositionPunch = MessageEnumTraits(8, 'CommandFloatPositionPunch')
CommandFloatPositionMinTarget = MessageEnumTraits(9, 'CommandFloatPositionMinTarget')
CommandFloatPositionMaxTarget = MessageEnumTraits(10, 'CommandFloatPositionMaxTarget')
CommandFloatPositionTargetLowpass = MessageEnumTraits(11, 'CommandFloatPositionTargetLowpass')
CommandFloatPositionMinOutput = MessageEnumTraits(12, 'CommandFloatPositionMinOutput')
CommandFloatPositionMaxOutput = MessageEnumTraits(13, 'CommandFloatPositionMaxOutput')
CommandFloatPositionOutputLowpass = MessageEnumTraits(14, 'CommandFloatPositionOutputLowpass')
CommandFloatVelocityKp = MessageEnumTraits(15, 'CommandFloatVelocityKp')
CommandFloatVelocityKi = MessageEnumTraits(16, 'CommandFloatVelocityKi')
CommandFloatVelocityKd = MessageEnumTraits(17, 'CommandFloatVelocityKd')
CommandFloatVelocityFeedForward = MessageEnumTraits(18, 'CommandFloatVelocityFeedForward')
CommandFloatVelocityDeadZone = MessageEnumTraits(19, 'CommandFloatVelocityDeadZone')
CommandFloatVelocityIClamp = MessageEnumTraits(20, 'CommandFloatVelocityIClamp')
CommandFloatVelocityPunch = MessageEnumTraits(21, 'CommandFloatVelocityPunch')
CommandFloatVelocityMinTarget = MessageEnumTraits(22, 'CommandFloatVelocityMinTarget')
CommandFloatVelocityMaxTarget = MessageEnumTraits(23, 'CommandFloatVelocityMaxTarget')
CommandFloatVelocityTargetLowpass = MessageEnumTraits(24, 'CommandFloatVelocityTargetLowpass')
CommandFloatVelocityMinOutput = MessageEnumTraits(25, 'CommandFloatVelocityMinOutput')
CommandFloatVelocityMaxOutput = MessageEnumTraits(26, 'CommandFloatVelocityMaxOutput')
CommandFloatVelocityOutputLowpass = MessageEnumTraits(27, 'CommandFloatVelocityOutputLowpass')
CommandFloatEffortKp = MessageEnumTraits(28, 'CommandFloatEffortKp')
CommandFloatEffortKi = MessageEnumTraits(29, 'CommandFloatEffortKi')
CommandFloatEffortKd = MessageEnumTraits(30, 'CommandFloatEffortKd')
CommandFloatEffortFeedForward = MessageEnumTraits(31, 'CommandFloatEffortFeedForward')
CommandFloatEffortDeadZone = MessageEnumTraits(32, 'CommandFloatEffortDeadZone')
CommandFloatEffortIClamp = MessageEnumTraits(33, 'CommandFloatEffortIClamp')
CommandFloatEffortPunch = MessageEnumTraits(34, 'CommandFloatEffortPunch')
CommandFloatEffortMinTarget = MessageEnumTraits(35, 'CommandFloatEffortMinTarget')
CommandFloatEffortMaxTarget = MessageEnumTraits(36, 'CommandFloatEffortMaxTarget')
CommandFloatEffortTargetLowpass = MessageEnumTraits(37, 'CommandFloatEffortTargetLowpass')
CommandFloatEffortMinOutput = MessageEnumTraits(38, 'CommandFloatEffortMinOutput')
CommandFloatEffortMaxOutput = MessageEnumTraits(39, 'CommandFloatEffortMaxOutput')
CommandFloatEffortOutputLowpass = MessageEnumTraits(40, 'CommandFloatEffortOutputLowpass')
CommandFloatSpringConstant = MessageEnumTraits(41, 'CommandFloatSpringConstant')
CommandFloatReferencePosition = MessageEnumTraits(42, 'CommandFloatReferencePosition')
CommandFloatReferenceEffort = MessageEnumTraits(43, 'CommandFloatReferenceEffort')
# CommandHighResAngleField
CommandHighResAnglePosition = MessageEnumTraits(0, 'CommandHighResAnglePosition')
CommandHighResAnglePositionLimitMin = MessageEnumTraits(1, 'CommandHighResAnglePositionLimitMin')
CommandHighResAnglePositionLimitMax = MessageEnumTraits(2, 'CommandHighResAnglePositionLimitMax')
# CommandNumberedFloatField
CommandNumberedFloatDebug = MessageEnumTraits(0, 'CommandNumberedFloatDebug')
# CommandBoolField
CommandBoolPositionDOnError = MessageEnumTraits(0, 'CommandBoolPositionDOnError')
CommandBoolVelocityDOnError = MessageEnumTraits(1, 'CommandBoolVelocityDOnError')
CommandBoolEffortDOnError = MessageEnumTraits(2, 'CommandBoolEffortDOnError')
# CommandStringField
CommandStringName = MessageEnumTraits(0, 'CommandStringName',
                                      allow_broadcast=False,
                                      not_bcastable_reason='Cannot set same '
                                      'name for all modules in a group.')
CommandStringFamily = MessageEnumTraits(1, 'CommandStringFamily')
# CommandFlagField
CommandFlagSaveCurrentSettings = MessageEnumTraits(0, 'CommandFlagSaveCurrentSettings')
CommandFlagReset = MessageEnumTraits(1, 'CommandFlagReset')
CommandFlagBoot = MessageEnumTraits(2, 'CommandFlagBoot')
CommandFlagStopBoot = MessageEnumTraits(3, 'CommandFlagStopBoot')
# CommandEnumField
CommandEnumControlStrategy = MessageEnumTraits(0, 'CommandEnumControlStrategy',
                                               yields_dict={
                                                 0 : 'Off',
                                                 1 : 'DirectPWM',
                                                 2 : 'Strategy2',
                                                 3 : 'Strategy3',
                                                 4 : 'Strategy4'})
# CommandIoBankField
CommandIoBankA = MessageEnumTraits(0, 'CommandIoBankA')
CommandIoBankB = MessageEnumTraits(1, 'CommandIoBankB')
CommandIoBankC = MessageEnumTraits(2, 'CommandIoBankC')
CommandIoBankD = MessageEnumTraits(3, 'CommandIoBankD')
CommandIoBankE = MessageEnumTraits(4, 'CommandIoBankE')
CommandIoBankF = MessageEnumTraits(5, 'CommandIoBankF')
# CommandLedField
CommandLedLed = MessageEnumTraits(0, 'CommandLedLed')

# FeedbackFloatField
FeedbackFloatBoardTemperature = MessageEnumTraits(0, 'FeedbackFloatBoardTemperature')
FeedbackFloatProcessorTemperature = MessageEnumTraits(1, 'FeedbackFloatProcessorTemperature')
FeedbackFloatVoltage = MessageEnumTraits(2, 'FeedbackFloatVoltage')
FeedbackFloatVelocity = MessageEnumTraits(3, 'FeedbackFloatVelocity')
FeedbackFloatEffort = MessageEnumTraits(4, 'FeedbackFloatEffort')
FeedbackFloatVelocityCommand = MessageEnumTraits(5, 'FeedbackFloatVelocityCommand')
FeedbackFloatEffortCommand = MessageEnumTraits(6, 'FeedbackFloatEffortCommand')
FeedbackFloatDeflection = MessageEnumTraits(7, 'FeedbackFloatDeflection')
FeedbackFloatDeflectionVelocity = MessageEnumTraits(8, 'FeedbackFloatDeflectionVelocity')
FeedbackFloatMotorVelocity = MessageEnumTraits(9, 'FeedbackFloatMotorVelocity')
FeedbackFloatMotorCurrent = MessageEnumTraits(10, 'FeedbackFloatMotorCurrent')
FeedbackFloatMotorSensorTemperature = MessageEnumTraits(11, 'FeedbackFloatMotorSensorTemperature')
FeedbackFloatMotorWindingCurrent = MessageEnumTraits(12, 'FeedbackFloatMotorWindingCurrent')
FeedbackFloatMotorWindingTemperature = MessageEnumTraits(13, 'FeedbackFloatMotorWindingTemperature')
FeedbackFloatMotorHousingTemperature = MessageEnumTraits(14, 'FeedbackFloatMotorHousingTemperature')
# FeedbackHighResAngleField
FeedbackHighResAnglePosition = MessageEnumTraits(0, 'FeedbackHighResAnglePosition')
FeedbackHighResAnglePositionCommand = MessageEnumTraits(1, 'FeedbackHighResAnglePositionCommand')
# FeedbackNumberedFloatField
FeedbackNumberedFloatDebug = MessageEnumTraits(0, 'FeedbackNumberedFloatDebug')
# FeedbackUInt64Field
FeedbackUInt64SequenceNumber = MessageEnumTraits(0, 'FeedbackUInt64SequenceNumber')
FeedbackUInt64ReceiveTime = MessageEnumTraits(1, 'FeedbackUInt64ReceiveTime')
FeedbackUInt64TransmitTime = MessageEnumTraits(2, 'FeedbackUInt64TransmitTime')
FeedbackUInt64HardwareReceiveTime = MessageEnumTraits(3, 'FeedbackUInt64HardwareReceiveTime')
FeedbackUInt64HardwareTransmitTime = MessageEnumTraits(4, 'FeedbackUInt64HardwareTransmitTime')
FeedbackUInt64SenderId = MessageEnumTraits(5, 'FeedbackUInt64SenderId')
# FeedbackVector3fField
FeedbackVector3fAccelerometer = MessageEnumTraits(0, 'FeedbackVector3fAccelerometer')
FeedbackVector3fGyro = MessageEnumTraits(1, 'FeedbackVector3fGyro')
# FeedbackQuaternionfField
FeedbackQuaternionfOrientation = MessageEnumTraits(0, 'FeedbackQuaternionfOrientation')
# FeedbackEnumField
FeedbackEnumTemperatureState = MessageEnumTraits(0, 'FeedbackEnumTemperatureState')
FeedbackEnumMstopState = MessageEnumTraits(1, 'FeedbackEnumMstopState')
FeedbackEnumPositionLimitState = MessageEnumTraits(2, 'FeedbackEnumPositionLimitState')
FeedbackEnumVelocityLimitState = MessageEnumTraits(3, 'FeedbackEnumVelocityLimitState')
FeedbackEnumEffortLimitState = MessageEnumTraits(4, 'FeedbackEnumEffortLimitState')
FeedbackEnumCommandLifetimeState = MessageEnumTraits(5, 'FeedbackEnumCommandLifetimeState')
# FeedbackIoBankField
FeedbackIoBankA = MessageEnumTraits(0, 'FeedbackIoBankA')
FeedbackIoBankB = MessageEnumTraits(1, 'FeedbackIoBankB')
FeedbackIoBankC = MessageEnumTraits(2, 'FeedbackIoBankC')
FeedbackIoBankD = MessageEnumTraits(3, 'FeedbackIoBankD')
FeedbackIoBankE = MessageEnumTraits(4, 'FeedbackIoBankE')
FeedbackIoBankF = MessageEnumTraits(5, 'FeedbackIoBankF')
# FeedbackLedField
FeedbackLedLed = MessageEnumTraits(0, 'FeedbackLedLed')

# InfoFloatField
InfoFloatPositionKp = MessageEnumTraits(0, 'InfoFloatPositionKp')
InfoFloatPositionKi = MessageEnumTraits(1, 'InfoFloatPositionKi')
InfoFloatPositionKd = MessageEnumTraits(2, 'InfoFloatPositionKd')
InfoFloatPositionFeedForward = MessageEnumTraits(3, 'InfoFloatPositionFeedForward')
InfoFloatPositionDeadZone = MessageEnumTraits(4, 'InfoFloatPositionDeadZone')
InfoFloatPositionIClamp = MessageEnumTraits(5, 'InfoFloatPositionIClamp')
InfoFloatPositionPunch = MessageEnumTraits(6, 'InfoFloatPositionPunch')
InfoFloatPositionMinTarget = MessageEnumTraits(7, 'InfoFloatPositionMinTarget')
InfoFloatPositionMaxTarget = MessageEnumTraits(8, 'InfoFloatPositionMaxTarget')
InfoFloatPositionTargetLowpass = MessageEnumTraits(9, 'InfoFloatPositionTargetLowpass')
InfoFloatPositionMinOutput = MessageEnumTraits(10, 'InfoFloatPositionMinOutput')
InfoFloatPositionMaxOutput = MessageEnumTraits(11, 'InfoFloatPositionMaxOutput')
InfoFloatPositionOutputLowpass = MessageEnumTraits(12, 'InfoFloatPositionOutputLowpass')
InfoFloatVelocityKp = MessageEnumTraits(13, 'InfoFloatVelocityKp')
InfoFloatVelocityKi = MessageEnumTraits(14, 'InfoFloatVelocityKi')
InfoFloatVelocityKd = MessageEnumTraits(15, 'InfoFloatVelocityKd')
InfoFloatVelocityFeedForward = MessageEnumTraits(16, 'InfoFloatVelocityFeedForward')
InfoFloatVelocityDeadZone = MessageEnumTraits(17, 'InfoFloatVelocityDeadZone')
InfoFloatVelocityIClamp = MessageEnumTraits(18, 'InfoFloatVelocityIClamp')
InfoFloatVelocityPunch = MessageEnumTraits(19, 'InfoFloatVelocityPunch')
InfoFloatVelocityMinTarget = MessageEnumTraits(20, 'InfoFloatVelocityMinTarget')
InfoFloatVelocityMaxTarget = MessageEnumTraits(21, 'InfoFloatVelocityMaxTarget')
InfoFloatVelocityTargetLowpass = MessageEnumTraits(22, 'InfoFloatVelocityTargetLowpass')
InfoFloatVelocityMinOutput = MessageEnumTraits(23, 'InfoFloatVelocityMinOutput')
InfoFloatVelocityMaxOutput = MessageEnumTraits(24, 'InfoFloatVelocityMaxOutput')
InfoFloatVelocityOutputLowpass = MessageEnumTraits(25, 'InfoFloatVelocityOutputLowpass')
InfoFloatEffortKp = MessageEnumTraits(26, 'InfoFloatEffortKp')
InfoFloatEffortKi = MessageEnumTraits(27, 'InfoFloatEffortKi')
InfoFloatEffortKd = MessageEnumTraits(28, 'InfoFloatEffortKd')
InfoFloatEffortFeedForward = MessageEnumTraits(29, 'InfoFloatEffortFeedForward')
InfoFloatEffortDeadZone = MessageEnumTraits(30, 'InfoFloatEffortDeadZone')
InfoFloatEffortIClamp = MessageEnumTraits(31, 'InfoFloatEffortIClamp')
InfoFloatEffortPunch = MessageEnumTraits(32, 'InfoFloatEffortPunch')
InfoFloatEffortMinTarget = MessageEnumTraits(33, 'InfoFloatEffortMinTarget')
InfoFloatEffortMaxTarget = MessageEnumTraits(34, 'InfoFloatEffortMaxTarget')
InfoFloatEffortTargetLowpass = MessageEnumTraits(35, 'InfoFloatEffortTargetLowpass')
InfoFloatEffortMinOutput = MessageEnumTraits(36, 'InfoFloatEffortMinOutput')
InfoFloatEffortMaxOutput = MessageEnumTraits(37, 'InfoFloatEffortMaxOutput')
InfoFloatEffortOutputLowpass = MessageEnumTraits(38, 'InfoFloatEffortOutputLowpass')
InfoFloatSpringConstant = MessageEnumTraits(39, 'InfoFloatSpringConstant')
# InfoHighResAngleField
InfoHighResAnglePositionLimitMin = MessageEnumTraits(0, 'InfoHighResAnglePositionLimitMin')
InfoHighResAnglePositionLimitMax = MessageEnumTraits(1, 'InfoHighResAnglePositionLimitMax')
# InfoBoolField
InfoBoolPositionDOnError = MessageEnumTraits(0, 'InfoBoolPositionDOnError')
InfoBoolVelocityDOnError = MessageEnumTraits(1, 'InfoBoolVelocityDOnError')
InfoBoolEffortDOnError = MessageEnumTraits(2, 'InfoBoolEffortDOnError')
# InfoStringField
InfoStringName = MessageEnumTraits(0, 'InfoStringName', allow_broadcast=False)
InfoStringFamily = MessageEnumTraits(1, 'InfoStringFamily')
InfoStringSerial = MessageEnumTraits(2, 'InfoStringSerial')
# InfoFlagField
InfoFlagSaveCurrentSettings = MessageEnumTraits(0, 'InfoFlagSaveCurrentSettings')
# InfoEnumField
InfoEnumControlStrategy = MessageEnumTraits(0, 'InfoEnumControlStrategy')
InfoEnumCalibrationState = MessageEnumTraits(1, 'InfoEnumCalibrationState')
# InfoLedField
InfoLedLed = MessageEnumTraits(0, 'InfoLedLed')


# -----------------------------------------------------------------------------
# Load API on import
# -----------------------------------------------------------------------------


_hebi_c_version = '{0}.{1}'.format(HEBI_Library_Wrapper._c_min_major,
                               HEBI_Library_Wrapper._c_min_minor)
_handle = HEBI_Library_Wrapper(_init_hebi_library())
