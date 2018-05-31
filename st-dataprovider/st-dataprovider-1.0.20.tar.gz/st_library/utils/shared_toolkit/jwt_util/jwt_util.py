import json

import jwt
from jwt import InvalidTokenError


class JWTUtil(object):
    class InvalidTokenError(Exception):
        pass

    def __init__(self, jwt_token):
        self.jwt_token = jwt_token

    def decode(self, public_key, verify_exp=False):
        try:
            decoded = jwt.decode(self.jwt_token, public_key,
                                 algorithms='RS256', options={'verify_exp': verify_exp}, audience=['web_app'])
        except InvalidTokenError as e:
            raise self.InvalidTokenError(str(e))
        return decoded

    def authenticate(self, public_key):
        return self.decode(public_key, True)

    def extract_info_no_verify(self):
        return jwt.decode(self.jwt_token, verify=False)

    def extract_expiration_string_no_verify(self):
        decoded = self.extract_info_no_verify()
        return decoded['exp']

    def extract_expiration_string(self, public_key):
        decoded = self.decode(public_key)
        return decoded['exp']

    @staticmethod
    def encode(obj_or_filename, private_key_or_filename, obj_from_file=False, private_key_from_file=False):
        if obj_from_file:
            with open(obj_or_filename, 'r') as f:
                obj = json.load(f)
        else:
            obj = obj_or_filename

        if private_key_from_file:
            with open(private_key_or_filename, 'r') as f:
                private_key = f.read()
        else:
            private_key = private_key_or_filename

        return jwt.encode(obj, private_key, 'RS256')
