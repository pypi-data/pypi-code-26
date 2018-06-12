""" Builds Python documentation in Markdown format for the given Python package
and its descendants.
"""
import copy
import importlib
import itertools
import os

import yaml

from catnado_docgen import crawler, filewriter
from catnado_docgen.crawler import MODULE, CLASS, FUNCTION


ATTRIBUTES = 'attributes'
CLASSES = 'classes'
DOCSTRING = 'docstring'
FUNCTIONS = 'functions'
NAME = 'name'
VALUE = 'value'

DOCGEN_API = 'docgen-api'
DOCS_DIR = 'docs_dir'
DEFAULT_DOCS_DIR = 'docs'
ERROR_IMPORT_FAILURE = 'Error: failed to import {}. Module must be importable to build docs.'
ERROR_OUTPUT_TARGET = 'output_target must specify a mkdocs.yml file or an existing directory'
ERROR_PAGES_YML = '--update-pages requires a mkdocs.yml file'
MKDOCS_YML = 'mkdocs.yml'
PAGES = 'pages'


def build_pages_config(mkdocs_config, packages, modules):
  """ Delete any old documentation from an existing pages entry, if it exists,
  and return a configuration containing the new documentation entries that can
  be converted to YAML.

  Args:
    mkdocs_config: existing configuration from `mkdocs.yml`
    packages: list of package names
    modules: list of module names
  Returns:
    `list` of pages (formatted as `dict`s)
  """
  pages_config = filter(
    lambda pages_dict: DOCGEN_API not in pages_dict,
    mkdocs_config.get(PAGES, [])
  ) if mkdocs_config else []

  doc_pages_config = _build_pages_config(packages, modules)

  # mkdocs wants every page entry to be a list with a one-entry dict for some
  # reason, so this converts our normal dictionary to a weird dictionary
  def fix_entries_recursively(page_dict_entry):
    new_list = []

    if isinstance(page_dict_entry, list):
      for entry in page_dict_entry:
        new_list.append(fix_entries_recursively(entry))

    elif isinstance(page_dict_entry, dict):
      for key, value in page_dict_entry.items():
        new_list.append({key: fix_entries_recursively(value)})

    if new_list:
      return sorted(new_list, key=lambda entry: entry.keys()[0])

    return page_dict_entry

  pages_config += fix_entries_recursively(doc_pages_config)

  return pages_config


def _build_pages_config(packages, modules):
  """ Build a new pages configuration for generated documentation.
  Args:
    packages: a list of package names
    modules: a list of module names
  Returns:
    `list`; `pages` configuration that can be merged into a `mkdocs.yml` file
  """
  # package or module names => dict (package) or None (module)
  package_dict = {}

  # set up initial structure in `package_dict`
  for package in packages:

    cv = package_dict
    for package_part in package.split('.'):
      # Add an overview page for each package as a default value
      cv = cv.setdefault(package_part, {
        '__init__': os.path.join(DOCGEN_API, '{}.md'.format(package))
      })

  # add docs for one page per module in each package
  for module in modules:

    cv = package_dict
    for module_part in module.split('.')[:-1]:
      cv = cv[module_part]

    cv[module.split('.')[-1]] = os.path.join(DOCGEN_API, '{}.md'.format(module))

  return {
    DOCGEN_API: package_dict,
  }


def _get_output_targets(output_target):
  """ Get the output directory and mkdocs.yml file location, iff applicable.
  
  Args:
    output_target: str; either output directory or mkdocs.yml file
  Returns:
    tuple of strings (output directory, mkdocs yaml file)
  Raises:
    ValueError: if validation on the output directory or mkdocs.yml file fails
  """
  if os.path.isfile(output_target):
    if os.path.split(output_target)[1] != MKDOCS_YML:
      raise ValueError(ERROR_OUTPUT_TARGET)

    mkdocs_config = yaml.load(file(output_target, 'r'))
    if not mkdocs_config:
      raise ValueError('Failed to load mkdocs.yml file')

    mkdocs_yml_dir = os.path.dirname(output_target)

    output_dir = os.path.join(
      mkdocs_yml_dir,
      mkdocs_config.get(DOCS_DIR, DEFAULT_DOCS_DIR),
      DOCGEN_API
    )

    # create the output directory if it does not exist
    if not os.path.exists(output_dir):
      os.mkdir(output_dir)

  elif os.path.isdir(output_target):
    mkdocs_config = None
    if args.update_pages:
      raise ValueError(ERROR_PAGES_YML)
    if not os.path.exists(output_target):
      raise ValueError(ERROR_OUTPUT_TARGET)
    output_dir = output_target

  else:
    raise ValueError(ERROR_OUTPUT_TARGET)

  return output_dir, mkdocs_config


def _get_attr_template_kwargs(attr):
  """ Get template kwargs for an attribute (like a string constant in a module)

  Args:
    attr: attribute name
  Returns:
    dict of template kwargs
  """
  return {
    NAME: attr,
  }


def _get_func_template_kwargs(func):
  """ Get template kwargs for a function object

  Args:
    class_: class object
  Returns:
    dict of template kwargs
  """
  return {
    NAME: func.__name__,
    DOCSTRING: func.__doc__,
  }


def _get_class_template_kwargs(class_):
  """ Get template kwargs for a class object

  Args:
    class_: class object
  Returns:
    dict of template kwargs
  """
  categorized_members = crawler.categorize_members(class_)
  stuff = {
    NAME: class_.__name__,
    DOCSTRING: class_.__doc__,
    FUNCTIONS: [
      _get_func_template_kwargs(class_.__dict__[func])
      for func in categorized_members.get(FUNCTION, [])
    ]
  }
  return stuff


def _get_module_template_kwargs(module):
  """ Get the template kwargs to pass to module.md

  Returns:
    dict of template kwargs
  """
  module_template_kwargs = {
    MODULE: module,
    ATTRIBUTES: [],
    CLASSES: [],
    FUNCTIONS: [],
  }

  categorized_members = crawler.categorize_members(module)

  for category, list_of_names in categorized_members.iteritems():
    for name in list_of_names:

      # don't document related modules for now
      if category == MODULE:
        continue

      value = getattr(module, name)

      if category == CLASS:
        if value.__module__ == module.__name__:
          module_template_kwargs[CLASSES].append(_get_class_template_kwargs(value))

      elif category == FUNCTION:
        module_template_kwargs[FUNCTIONS].append(_get_func_template_kwargs(value))

      else:
        module_template_kwargs[ATTRIBUTES].append(_get_attr_template_kwargs(name))

  return module_template_kwargs


def main(args):
  """ See __main__.py for exhaustive list of arguments.

  `output_target` is either a `mkdocs.yml` file or a directory in which to dump
  the markdown files.

  If a `mkdocs.yml` file is provided, `--update-pages` will
  automatically update it with the newly-generated documentation.

  Raises:
    ValueError: if specified output target is invalid or specified mkdocs.yml file
      cannot be loaded.
  """
  output_dir, mkdocs_config = _get_output_targets(args.output_target)

  try:
    root_package = importlib.import_module(args.root_package)
  except ImportError:
    print ERROR_IMPORT_FAILURE.format(args.root_package)
    return

  packages, modules = crawler.get_modules_and_packages_to_document(root_package)

  # importing a package is essentially importing it's __init__ as a module, so
  # create a file for each package as well as module
  for module_name in itertools.chain(packages, modules):
    module = importlib.import_module(module_name)
    output_file = os.path.join(output_dir, '{}.md'.format(module.__name__))
    template_kwargs = _get_module_template_kwargs(module)
    filewriter.render_module_markdown(template_kwargs, output_file)

  if args.update_pages or args.print_pages:
    pages_config = build_pages_config(mkdocs_config, packages, modules)

    if args.update_pages:
      assert mkdocs_config is not None, ERROR_PAGES_YML
      mkdocs_config[PAGES] = pages_config
      with open(args.output_target, 'w') as output_file:
        output_file.write(yaml.dump(mkdocs_config, default_flow_style=False))

    elif args.print_pages:
      print yaml.dump(pages_config, default_flow_style=False)
