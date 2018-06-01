from django.conf import settings
from rest_framework.settings import APISettings
from rest_framework_jwt.settings import api_settings as jwt_api_settings

USER_SETTINGS = getattr(settings, 'AUTH0', None)

DEFAULTS = {
    'ALGORITHM': 'RS256',
    'CLIENT_ID': getattr(settings, 'AUTH0_CLIENT_ID', None),
    'CLIENT_ID_LIST': getattr(settings, 'AUTH0_CLIENT_ID_LIST', None),
    'DOMAIN': getattr(settings, 'AUTH0_DOMAIN', None),
    'JWT_AUTH_HEADER_PREFIX': 'JWT',
    'USERNAME_FIELD': 'email',
    'JWT_PAYLOAD_GET_USERNAME_HANDLER':
    'pyauth0jwtrest.utils.auth0_get_username_from_payload_handler',
    'CREATE_USERS': True,
    'CLIENT_SECRET_BASE64_ENCODED': True,
    'CLIENT_SECRET': getattr(settings, 'AUTH0_CLIENT_SECRET', None),
}

# List of settings that may be in string import notation.
IMPORT_STRINGS = (
    'JWT_PAYLOAD_GET_USERNAME_HANDLER',
)

auth0_api_settings = APISettings(USER_SETTINGS, DEFAULTS, IMPORT_STRINGS)
jwt_api_settings.JWT_PAYLOAD_GET_USERNAME_HANDLER = auth0_api_settings.JWT_PAYLOAD_GET_USERNAME_HANDLER
