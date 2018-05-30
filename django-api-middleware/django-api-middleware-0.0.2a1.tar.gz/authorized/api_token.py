"""
================
API Token Module
================
Token handling, in charge of creating, verifying, and decoding certain token.
"""
from datetime import datetime, timedelta
import jwt
from authorized import api_utils
def generate():
    r"""
    Generates a token using the jwt library.
    The token signature requires a 'Key' that must be set in any of two places
    Project Settings or environment variable with name API_KEY
    :return: jwt_token value that must be appended on headers on each request.
    """
    token = jwt.encode({'app_name': api_utils.get_name(),
        'exp': datetime.utcnow() + timedelta(seconds=10),
        'iat': datetime.utcnow(),
        'nbf': datetime.utcnow()
        }, api_utils.get_key(),
        algorithm='HS512').decode('utf-8')
    return token

def verify(token):
    r"""
    Verifies a given token to match the project requirements and decoded the values.
    :param token: a token to be verified and decoded
    :return: dictionary containing a validation status and the name of the application that was placed in the payload.
    """
    response = {}
    response['is_valid'] = False
    try:
        decoded_data = jwt.decode(token,
                                api_utils.get_key(),
                                verify=True,
                                algorithms='HS512',
                                options={'verify_iat': True, 'require_exp':True, 'require_iat': True, 'require_nbf': True})
        response['is_valid'] = True
        response['app_name'] = decoded_data['app_name']
    except jwt.exceptions.InvalidSignatureError:
        # token was signed with a non valid key.
        response['message'] = 'Invalid token.'
    except jwt.exceptions.DecodeError:
        # token has been altered
        response['message'] = 'Invalid token.'
    except jwt.exceptions.ExpiredSignatureError:
        # token has expired
        response['message'] = 'Invalid token'
    except jwt.exceptions.InvalidIssuedAtError:
        # 'issued at' claim has a future date. token has been manipulated.
        response['message'] = 'Invalid token'
    except jwt.exceptions.MissingRequiredClaimError:
        # a claim that is required has not been sent
        response['message'] = 'Invalid payload'
    except jwt.exceptions.InvalidTokenError:
        # invalid token generic exception
        response['message'] = 'Invalid token.'
    return response
