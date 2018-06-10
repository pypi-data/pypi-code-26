from catnado.utils.jinja import get_jinja_environment
from webapp2 import RequestHandler


CONTENT_TYPE = 'Content-Type'
CONTENT_TYPE_HTML = 'text/html'


class StaticPageHandler(RequestHandler):
  """Handler for serving a microservice's internal API.

  Ensures that incoming requests are coming from within the same application by
  verifying that the X-Appengine-Inbound-Appid matches the current application's
  ID.
  """

  PACKAGE = 'catnado'
  TEMPLATES_PATH = 'templates'

  def __init__(self):
    super(StaticPageHandler, self).__init__()
    self.jinja_env = None

  def jinja_render(self, template, kwargs):
    """Set Content-Type and write JSON data in a response.

    Arguments:
      kwargs: a dict to pass to the Jinja template
    """
    self.response.headers[CONTENT_TYPE] = CONTENT_TYPE_HTML

    if not self.jinja_env:
      self.jinja_env = get_jinja_environment(self.PACKAGE, self.TEMPLATES_PATH)

    template = self.jinja_env.get_template(template)
    if template:
      self.response.out.write(template.render(**kwargs))
