from django.contrib.auth.models import User
from django.contrib import auth as django_auth
from django.contrib.auth import login
from django.conf import settings
from django.shortcuts import redirect
from django.contrib.auth import logout

import jwt
from furl import furl
import json
import base64
import logging
import requests
import jwcrypto.jwk as jwk

logger = logging.getLogger(__name__)


def public_user_auth_and_jwt(function):
    def wrap(request, *args, **kwargs):
        """
        Here we see if the user is logged in but let them stay on the page if they aren't.
        """

        # Validates the JWT and returns its payload if valid.
        jwt_payload = validate_request(request)

        # User is both logged into this app and via JWT.
        if request.user.is_authenticated() and jwt_payload is not None:
            return function(request, *args, **kwargs)
        # User has a JWT session open but not a Django session. Start a Django session and continue the request.
        elif not request.user.is_authenticated() and jwt_payload is not None:
            if jwt_login(request, jwt_payload):
                return function(request, *args, **kwargs)
            else:
                return function(request, *args, **kwargs)
        # User isn't logged in but that's okay.
        else:
            return function(request, *args, **kwargs)
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


def user_auth_and_jwt(function):
    def wrap(request, *args, **kwargs):

        # Validates the JWT and returns its payload if valid.
        jwt_payload = validate_request(request)

        # User is both logged into this app and via JWT.
        if request.user.is_authenticated() and jwt_payload is not None:

            # Ensure the email matches (without case sensitivity)
            if request.user.username.lower() != jwt_payload['email'].lower():
                logger.warning('Django and JWT email mismatch! Log them out and redirect to log back in')
                return logout_redirect(request)

            return function(request, *args, **kwargs)
        # User has a JWT session open but not a Django session. Start a Django session and continue the request.
        elif not request.user.is_authenticated() and jwt_payload is not None:
            if jwt_login(request, jwt_payload):
                return function(request, *args, **kwargs)
            else:
                return logout_redirect(request)
        # User doesn't pass muster, throw them to the login app.
        else:
            return logout_redirect(request)
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


def validate_jwt(request):
    """
    Determines if the JWT is valid based on expiration and signature evaluation.
    :param request: 
    :return: None if JWT is invalid or missing.
    """
    # Extract JWT token into a string.
    jwt_string = request.COOKIES.get("DBMI_JWT", None)

    # Check that we actually have a token.
    if jwt_string is not None:

        # Attempt to validate the JWT (Checks both expiry and signature)
        try:
            payload = jwt.decode(jwt_string,
                                 base64.b64decode(settings.AUTH0_SECRET, '-_'),
                                 algorithms=['HS256'],
                                 leeway=120,
                                 audience=settings.AUTH0_CLIENT_ID)

        except jwt.InvalidTokenError as err:
            logger.error(str(err))
            logger.error("[PYAUTH0JWT][DEBUG][validate_jwt] - Invalid JWT Token.")
            payload = None
        except jwt.ExpiredSignatureError as err:
            logger.error(str(err))
            logger.error("[PYAUTH0JWT][DEBUG][validate_jwt] - JWT Expired.")
            payload = None
    else:
        payload = None

    return payload


def validate_request(request):
    # Extract JWT token into a string.
    jwt_string = request.COOKIES.get("DBMI_JWT", None)

    # Check that we actually have a token.
    if jwt_string is not None:
        return validate_rs256_jwt(jwt_string)
    else:
        return None


def retrieve_public_key(jwt_string):

    try:
        jwks = get_public_keys_from_auth0()

        unverified_header = jwt.get_unverified_header(str(jwt_string))

        rsa_key = {}

        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"]
                }

        return rsa_key
    except KeyError as e:
        logger.debug('Could not compare keys, probably old HS256 session')
        logger.exception(e)

    return None


def get_public_keys_from_auth0():
    jwks_return = requests.get("https://" + settings.AUTH0_DOMAIN + "/.well-known/jwks.json")
    jwks = jwks_return.json()

    return jwks


def validate_rs256_jwt(jwt_string):

    rsa_pub_key = retrieve_public_key(jwt_string)
    payload = None

    if rsa_pub_key:
        jwk_key = jwk.JWK(**rsa_pub_key)

        # Determine which Auth0 Client ID (aud) this JWT pertains to.
        try:
            auth0_client_id = str(jwt.decode(jwt_string, verify=False)['aud'])
        except Exception as e:
            logger.error('[PYAUTH0JWT][DEBUG][validate_rs256_jwt] - Failed to get the aud from jwt payload')
            return None

        # Check that the Client ID is in the allowed list of Auth0 Client IDs for this application
        allowed_auth0_client_id_list = settings.AUTH0_CLIENT_ID_LIST
        if auth0_client_id not in allowed_auth0_client_id_list:
            logger.error('[PYAUTH0JWT][DEBUG][validate_rs256_jwt] - Auth0 Client ID not allowed')
            return None

        # Attempt to validate the JWT (Checks both expiry and signature)
        try:
            payload = jwt.decode(jwt_string,
                                 jwk_key.export_to_pem(private_key=False),
                                 algorithms=['RS256'],
                                 leeway=120,
                                 audience=auth0_client_id)

        except jwt.InvalidTokenError as err:
            logger.error(str(err))
            logger.error("[PYAUTH0JWT][DEBUG][validate_rs256_jwt] - Invalid JWT Token.")
            payload = None
        except jwt.ExpiredSignatureError as err:
            logger.error(str(err))
            logger.error("[PYAUTH0JWT][DEBUG][validate_rs256_jwt] - JWT Expired.")
            payload = None

    return payload


def jwt_login(request, jwt_payload):
    """
    The user has a valid JWT but needs to log into this app. Do so here and return the status.
    :param request:
    :param jwt_payload: String form of the JWT.
    :return:
    """

    logger.debug("[PYAUTH0JWT][DEBUG][jwt_login] - Logging user in via JWT. Is Authenticated? " + str(request.user.is_authenticated()))

    request.session['profile'] = jwt_payload

    user = django_auth.authenticate(**jwt_payload)

    if user:
        login(request, user)
    else:
        logger.error("[PYAUTH0JWT][DEBUG][jwt_login] - Could not log user in.")

    return request.user.is_authenticated()


def logout_redirect(request):
    """
    This will log a user out and redirect them to log in again via the AuthN server.
    :param request: 
    :return: The response object that takes the user to the login page. 'next' parameter set to bring them back to their intended page.
    """
    logout(request)

    # Build the URL
    login_url = furl(settings.AUTHENTICATION_LOGIN_URL)
    login_url.query.params.add('next', request.build_absolute_uri())

    # Check for branding
    if hasattr(settings, 'SCIAUTH_BRANDING'):
        logger.debug('SciAuth branding passed')

        # Encode it and pass it
        branding = base64.urlsafe_b64encode(json.dumps(settings.SCIAUTH_BRANDING).encode('utf-8')).decode('utf-8')
        login_url.query.params.add('branding', branding)

    # Set the URL and purge cookies
    response = redirect(login_url.url)
    response.delete_cookie('DBMI_JWT', domain=settings.COOKIE_DOMAIN)
    logger.debug('Redirecting to: {}'.format(login_url.url))

    return response


class Auth0Authentication(object):

    def authenticate(self, **token_dictionary):
        logger.debug("[PYAUTH0JWT][DEBUG][authenticate] - Attempting to Authenticate User.")

        try:
            user = User.objects.get(username=token_dictionary["email"])
        except User.DoesNotExist:
            logger.debug("[PYAUTH0JWT][DEBUG][authenticate] - User not found, creating.")

            user = User(username=token_dictionary["email"], email=token_dictionary["email"])
            user.save()
        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


