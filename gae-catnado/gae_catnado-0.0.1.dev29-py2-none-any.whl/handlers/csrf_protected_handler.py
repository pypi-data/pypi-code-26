from catnado.handlers import CatnadoHandler
from catnado.utils.csrf import validate_csrf_token


class CSRFProtectedHandler(CatnadoHandler):
  """SimplePublicHandler that requires a CSRF token on POST."""

  CSRF_PROTECTED_METHODS = {'POST', 'PUT', 'DELETE'}

  def dispatch(self):
    """Override dispatch to CSRF-validate POST requests."""
    if self.request.method in self.CSRF_PROTECTED_METHODS:
      if not validate_csrf_token(self):
        self.abort(403)

    super(CSRFProtectedHandler, self).dispatch()
