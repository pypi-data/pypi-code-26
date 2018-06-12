import binascii
import os
import time


CSRF_TOKEN_FORM_KEY = '_csrf_token'
CSRF_TOKEN_COOKIE_KEY = 'cf53b32a803ef1cbee5ba32d7c062c716567234b1441de16a79c602456c61163'


def get_csrf_token(request, response):
  """Get a CSRF token to embed in an HTML page.

  The token is also stored in a Cookie and verified upon POST/PUT.

  Arguments:
    request: webapp2 Request object
    response: webapp2 Response object

  Returns:
    str; a CSRF token, having been saved to the Cookie
  """
  csrf_token = request.cookies.get(CSRF_TOKEN_COOKIE_KEY)

  if not csrf_token:
    csrf_token = _generate_csrf_token()
    _store_token_in_cookie(csrf_token, response)

  return csrf_token


def _store_token_in_cookie(csrf_token, response):
  """Store the given token in a Cookie on the response."""
  response.set_cookie(
    CSRF_TOKEN_COOKIE_KEY,
    csrf_token,
    max_age=3600,
    path='/',
  )


def _generate_csrf_token():
  """Generate a random CSRF token including the current time."""
  random_token = binascii.hexlify(os.urandom(32))
  now = int(time.time())
  return '{}-{}'.format(random_token, now)


def csrf_token_required():
  """Use as a decorator to protect handler functions from CSRF attacks."""
  def outer_decorator(func):
    def inner_decorator(self, *args, **kwargs):

      csrf_token_form = self.request.get(CSRF_TOKEN_FORM_KEY)
      csrf_token_cookie = self.request.cookies.get(CSRF_TOKEN_COOKIE_KEY)
      if not csrf_token_form or not csrf_token_cookie:
        self.abort(403)

      if csrf_token_form != csrf_token_cookie:
        self.abort(403)

      func(self, *args, **kwargs)

    return inner_decorator

  return outer_decorator
