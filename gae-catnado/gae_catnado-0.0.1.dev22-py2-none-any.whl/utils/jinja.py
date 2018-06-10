from jinja2 import Environment, FileSystemLoader


def get_jinja_environment(package_name, package_path='templates'):
  """Get a Jinja environment for rendering a template.

  Args:
    template_dir: required str; base location of templates
  """
  return Environment(
    loader=FileSystemLoader(package_name, package_path),
  )
