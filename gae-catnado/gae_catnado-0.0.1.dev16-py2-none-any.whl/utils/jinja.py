from jinja2 import Environment, PackageLoader, select_autoescape


def get_jinja_environment(package_name, package_path='templates'):
  """Get a Jinja environment for rendering a template.

  Args:
    template_dir: required str; base location of templates
  """
  return Environment(
    loader=PackageLoader(package_name, package_path),
    autoescape=select_autoescape(['html']),
  )
