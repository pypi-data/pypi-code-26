import base64


class AuthenticateMixin(object):

    def __init__(self):
        header_autorization = f"{self.smartbill_user}:{self.smartbill_token}".encode("utf-8")
        header_autorization_base64 = base64.b64encode(header_autorization).decode("utf-8")
        self.headers = {"authorization": f'Basic {header_autorization_base64}',
                        'Content-Type': 'application/json'}
        super().__init__()
