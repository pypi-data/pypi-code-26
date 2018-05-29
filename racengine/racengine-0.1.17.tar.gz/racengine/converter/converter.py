import requests
from racengine.email_sender.sender import prepare_and_send


class Converter(object):
    def __init__(self, converter_endpoint=None, smtp_server=None):
        self.__converter_endpoint = converter_endpoint
        self.__smtp_server = smtp_server

    def run(self, file_to_convert, email_prop=None, output_format='pdf', send_email=False):
        url = self.__converter_endpoint
        file = {'file': file_to_convert}

        req = requests.post(url, files=file)
        if req.status_code == 200:
            file_bytes = req.content()
            result = True

            if email_prop and send_email:
                email_prop.update({'file': file_bytes})
                email_prop.update({'file_type': output_format})
                result = prepare_and_send(email_prop, self.__smtp_server)
            return result, file_bytes

        return False, None