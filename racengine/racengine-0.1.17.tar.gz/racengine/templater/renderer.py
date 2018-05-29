import requests
from racengine.email_sender.sender import prepare_and_send


class Renderer(object):
    def __init__(self, templater_endpoint=None, smtp_server=None):
        self.__templater_endpoint = templater_endpoint
        self.__smtp_server = smtp_server

    def run(self, template, data, email_prop=None, send_email=False):
        url = self.__templater_endpoint
        data_to_post = {'data': data}
        file = {'file': template}

        req = requests.post(url, data=data_to_post, files=file)
        if req.status_code == 200:
            docx_bytes = req.content()
            result = True

            if email_prop and send_email:
                email_prop.update({'file': docx_bytes})
                email_prop.update({'file_type': 'docx'})
                result = prepare_and_send(email_prop, self.__smtp_server)
            return result, docx_bytes

        return False, None