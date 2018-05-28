from yangsgoogle.credentials import CredentialManager, ServiceMap
from yangsutil import LogUtil
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
import mimetypes
import base64
import os

SERVICE = {
    'version': 'v1',
    'scope': [
        'https://mail.google.com/'
    ]
}


class YangsGoogleMail:
    def __init__(self, app_name, user_name, credential_root, logger=None):
        self.logger = LogUtil.get_logger(app_name=app_name) if logger is None else logger

        self.service = CredentialManager(logger=self.logger).service(
            service_name=ServiceMap.GMAIL,
            app_name=app_name,
            user_name=user_name,
            credential_root=credential_root
        )

    # public
    def send(self, option, subject, content, _subtype='plain'):
        message = MIMEText(content, _subtype)

        message['subject'] = subject
        message['to'] = option['to']

        try:
            message['from'] = option['from']
        except KeyError:
            message['from'] = 'admin@webmaster.com'

        try:
            message['cc'] = option['cc']
        except KeyError:
            pass

        message_body = {
            'raw': base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        }

        return self.service.users().messages().send(userId="me", body=message_body).execute()

    def send_with_file(self, option, subject, content, file, _subtype='plain'):
        message = MIMEMultipart()
        message['subject'] = subject
        message['to'] = option['to']

        try:
            message['from'] = option['from']
        except KeyError:
            message['from'] = 'admin@webmaster.com'

        try:
            message['cc'] = option['cc']
        except KeyError:
            pass

        msg = MIMEText(content, _subtype)
        message.attach(msg)

        content_type, encoding = mimetypes.guess_type(file)

        if content_type is None or encoding is not None:
            content_type = 'application/octet-stream'

        main_type, sub_type = content_type.split('/', 1)
        if main_type == 'text':
            fp = open(file, 'rb')
            msg = MIMEText(fp.read(), _subtype=sub_type)
            fp.close()
        elif main_type == 'image':
            fp = open(file, 'rb')
            msg = MIMEImage(fp.read(), _subtype=sub_type)
            fp.close()
        elif main_type == 'audio':
            fp = open(file, 'rb')
            msg = MIMEAudio(fp.read(), _subtype=sub_type)
            fp.close()
        else:
            fp = open(file, 'rb')
            msg = MIMEBase(main_type, sub_type)
            msg.set_payload(fp.read())
            fp.close()

        filename = os.path.basename(file)
        msg.add_header('Content-Disposition', 'attachment', filename=filename)
        message.attach(msg)

        message_body = {
            'raw': base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        }

        return self.service.users().messages().send(userId="me", body=message_body).execute()
