import requests
from cryptography.x509 import load_pem_x509_certificate
from cryptography.hazmat.backends import default_backend

from django.utils.encoding import smart_text
from django.utils.translation import ugettext as _
from rest_framework import exceptions
from rest_framework.authentication import get_authorization_header

from pyauth0jwtrest.settings import auth0_api_settings


# Handlers --------------------------------------------------------------------
def auth0_get_username_from_payload_handler(payload):
    username = payload.get(auth0_api_settings.USERNAME_FIELD)
    return username


# Authorization Utils ---------------------------------------------------------
def get_jwt_value(request):
    auth = get_authorization_header(request).split()
    auth_header_prefix = auth0_api_settings.JWT_AUTH_HEADER_PREFIX.lower()

    if not auth or smart_text(auth[0].lower()) != auth_header_prefix:
        return None

    if len(auth) == 1:
        msg = _('Invalid Authorization header. No credentials provided.')
        raise exceptions.AuthenticationFailed(msg)
    elif len(auth) > 2:
        msg = _('Invalid Authorization header. Credentials string '
                'should not contain spaces.')
        raise exceptions.AuthenticationFailed(msg)

    return auth[1]


def get_auth0_public_key(auth0_domain):

    # Get the pub key from the endpoint
    jwk_json = requests.get("https://" + auth0_domain + "/.well-known/jwks.json").json()

    # Build it from the JSON
    cert = '-----BEGIN CERTIFICATE-----\n' + jwk_json['keys'][0]['x5c'][0] + '\n-----END CERTIFICATE-----'
    certificate = load_pem_x509_certificate(str.encode(cert), default_backend())

    return certificate.public_key()


# Auth0 Metadata --------------------------------------------------------------
def get_app_metadata_from_payload(payload):
    app_metadata = payload.get('app_metadata')
    return app_metadata


def get_user_metadata_from_payload(payload):
    user_metadata = payload.get('user_metadata')
    return user_metadata
