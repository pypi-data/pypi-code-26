import json

from catnado.utils.api import InsecureAPIRequestError, validate_api_request
from webapp2 import RequestHandler


CONTENT_TYPE = 'Content-Type'
CONTENT_TYPE_JSON = 'application/json'


class ServiceAPIHandler(RequestHandler):
  """Handler for serving a microservice's internal API.

  Ensures that incoming requests are coming from within the same application by
  verifying that the X-Appengine-Inbound-Appid matches the current application's
  ID.
  """

  def dispatch(self):
    """Override dispatch to validate incoming requests are secure.

    A request is secure if its X-Appengine-Internal-Appid header matches the
    applications current application ID.
    """
    try:
      validate_api_request(self.request)

    except InsecureAPIRequestError:
      self.abort(403)

    super(ServiceAPIHandler, self).dispatch()

  def json_response(self, data):
    """Set Content-Type and write JSON data in a response.

    Arguments:
      data: a dict to JSON-stringify and return
    """
    self.response.headers[CONTENT_TYPE] = CONTENT_TYPE_JSON
    self.response.out.write(json.dumps(data))
