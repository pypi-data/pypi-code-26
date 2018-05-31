# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#
#  HEBI Core python API - Copyright 2018 HEBI Robotics
#  See https://hebi.us/softwarelicense for license details
#
# ------------------------------------------------------------------------------

from ._internal import log_file as _log_file
from ._internal import group as _group
from ._internal import raw as _raw

from os.path import isfile as _isfile

def create_imitation_group(size):
  """
  Create an imitation group of the provided size.
  The imitation group returned from this function provides the exact same
  interface as a group created from the :class:`Lookup` class.

  However, there are a few subtle differences between the imitation group and
  group returned from a lookup operation. See :ref:`imitation-group-contrast` section
  for more information.

  :param size: The number of modules in the imitation group
  :type size:  int
  
  :return: The imitation group. This will never be ``None``
  :rtype:  Group

  :raises ValueError: If size is less than 1
  """
  return _group.create_imitation_group(size)


def load_log(file):
  """
  Opens an existing log file.

  :param file: the path to an existing log file
  :type file:  str, unicode

  :return: The log file. This function will never return ``None``
  :rtype:  LogFile
  
  :raises TypeError: If file is an invalid type
  :raises IOError: If the file does not exist or is not a valid log file
  """
  try:
    f_exists = _isfile(file)
  except TypeError as t:
    raise TypeError('Invalid type for file. '
                    'Caught TypeError with message: {0}'.format(t.args))

  if not f_exists:
    raise IOError('file {0} does not exist'.format(file))

  log_file = _raw.hebiLogFileOpen(file.encode('utf-8'))
  if log_file is None:
    raise IOError('file {0} is not a valid log file'.format(file))

  return _log_file.LogFile(log_file)


def plot_logs(logs, fbk_field, modules=None):
  """
  Currently unimplemented. Do not use.

  :param fbk_field: Feedback field to plot
  :type fbk_field:  str, unicode

  :param modules: Optionally select which modules to plot
  :type modules: NoneType, list
  """
  if isinstance(logs, _log_file.LogFile):
    logs = [logs]

  raise NotImplementedError()


def plot_trajectory(trajectory, dt=0.01):
  """
  Currently unimplemented. Do not use.

  :param trajectory:
  :type trajectory:  Trajectory

  :param dt: Delta between points in trajectory to plot
  :type dt:  int, float
  """
  raise NotImplementedError()

