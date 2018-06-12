""" Module for crawling Python code and extracting what needs to be documented.
"""
import inspect
import pkgutil
from collections import defaultdict
from types import ModuleType


CLASS = 'class'
FUNCTION = 'function'
MODULE = 'module'


def categorize_module_member(module_item):
  """ Determine what the category of the given `module_item` is.

  This categorization will determine how documentation how docs are built
  item
  Categories include:
    - class

  Args:
    module_item: an object out of a module's `__dict__`
  Returns:
    string classifier
  """
  if inspect.isclass(module_item):
    return CLASS
  elif inspect.isfunction(module_item):
    return FUNCTION
  elif inspect.ismodule(module_item):
    return MODULE
  return type(module_item).__name__


def categorize_members(module_class_or_func, include_private=False):
  """ Get a mapping of key -> type for all items in the given module.

  Dunder items (those whose names begin and end with `__`) are never documented.

  Private items (those whose names begin with `_`) can be included in
  documentation by setting `include_private=True`.

  Args:
    module_class_or_func: module, class, or function whose members should be
      categorized
    include_private: optional bool, whether to include "private" variables (i.e.
      those whose names start with a leading underscore).
  Returns:
    `dict` mapping 'types' to lists of keys from `__dict__`, i.e...
    ```
    {
      'class': ['TestClass', 'OtherClass'],
      'function': ['test1', 'test2']
    }
    ```
  """
  keys_by_type = defaultdict(list)
  for key, value in module_class_or_func.__dict__.iteritems():
    if not key.startswith('__') and (not key.startswith('_') or include_private):
      keys_by_type[categorize_module_member(value)].append(key)
  return dict(keys_by_type)


def get_modules_and_packages_to_document(root_package):
  """ Get a list of module and package names to document.

  Args:
    root_package: module object from `importlib.import_module`
  Returns:
    tuple of package names (str), module names (str) beneath `root_package` that
    should be documented.
  """
  if not isinstance(root_package, ModuleType):
    raise TypeError('Expected root_package to be a ModuleType')

  is_module = not hasattr(root_package, '__path__')

  modules = []
  packages = [root_package.__name__]

  if is_module:
    # root package is actually just a module
    modules.append(root_package)
  else:
    path = root_package.__path__
    prefix = '{}.'.format(root_package.__name__)
    for _, name, is_pkg in pkgutil.walk_packages(path, prefix):
      if is_pkg:
        packages.append(name)
      else:
        modules.append(name)

  return packages, modules
