"""
    Copyright 2017 n.io Innovation, LLC | Patent Pending
"""
from pubkeeper.server.core.auth.base import PubkeeperAuthProvider
from pubkeeper.server.core.auth.error import PubkeeperAuthError
from pubkeeper.protocol.v1.packet import ErrorPacket
from tornado import gen
from tornado.httpclient import AsyncHTTPClient, HTTPRequest, HTTPError
from hashlib import sha256
import logging
import json
import jwt


class LocalAuthProvider(PubkeeperAuthProvider):
    def configure(self, config):
        self.client = AsyncHTTPClient()
        self.validate_url = config.get('validate')
        self._logger = logging.getLogger('pubkeeper.server.core.auth.local')

    def validate_request(self, token):
        query = HTTPRequest(
            url=self.validate_url,
            method="POST",
            body=json.dumps({'token': token}),
            headers={
                'Content-Type': 'application/json',
            }
        )

        return self.client.fetch(query)

    @gen.coroutine
    def validate_token(self, connection, token):
        # This is to track if a JWT was authenticated, at which point
        # we will want to alert the user that they need to update
        jwt_error = False

        try:
            response = yield self.validate_request(token)
        except HTTPError:
            try:
                jwt.decode(token, verify=False)
                token = sha256(token.encode()).hexdigest()
                response = yield self.validate_request(token)
                jwt_error = True
            except:
                self._logger.error("Auth Server Rejected Token")
                raise PubkeeperAuthError()

        if response.code == 200:
            try:
                body = json.loads(response.body.decode())
                if body['valid']:
                    if jwt_error:
                        connection._write_message(ErrorPacket(
                            "You have connected using a legacy JWT, and should"
                            " upgrade to a new SHA256 token"
                        ))

                    return body['rights']
            except:
                self._logger.error("Auth Server Accepted Token, however it "
                                   "provided an unknown response")
                raise PubkeeperAuthError()

        self._logger.error("Auth Server Rejected Token")
        raise PubkeeperAuthError()
