import jinja2


TEMPLATES_PATH = ['catnado_docgen', 'templates']


# "singleton"
env_instance = None


def _jinja_finalize(output):
  """ Provide a finalize function for Jinja that suppresses the output of `None`

  Returns:
    `output` or empty string (but not None)
  """
  return output if output else ''


def get_jinja_environment():
  """ Get the Jinja2 environment to use when rendering templates.

  One copy of the environment is kept at the module-level using `global`.

  Returns:
    jinja2.Environment
  """
  global env_instance
  if not env_instance:
    env_instance = jinja2.Environment(
      loader=jinja2.PackageLoader(*TEMPLATES_PATH),
      finalize=_jinja_finalize,
    )
  return env_instance


def render_module_markdown(template_kwargs, target_filename):
  """ Render a markdown file for the given module.

  Args:
    module: module object to render documentation for
    target: str filename
  Returns:
    str containing rendered template
  """
  env = get_jinja_environment()

  template = env.get_template('module.jinja.md')
  rendered_template = template.render(**template_kwargs)

  with open(target_filename, 'w') as output_file:
    output_file.write(rendered_template)
