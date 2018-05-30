import mimetypes
import email
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from racengine.email_sender.SMTPServer import SMTPException


def prepare_and_send(email_properties, smtp_server):

    msg = MIMEMultipart()
    msg['Subject'] = email_properties.get('subject', '')
    msg['From'] = email_properties.get('from_addr') or email_properties.get('From') or smtp_server.get('username')
    msg['To'] = email_properties.get('to_addr') or email_properties.get('To')
    msg['Cc'] = email_properties.get('cc') or email_properties.get('Cc')
    msg['Cci'] = email_properties.get('cci') or email_properties.get('Cci')
    msg['Date'] = email.utils.formatdate()

    joined_f_name = email_properties.get('joined_f_name', 'rapport')

    if not msg.get('To'):
        raise SMTPException("Recipient(s) e-mail(s) missing")

    if not msg.get('From'):
        raise SMTPException("Sender e-mail missing")

    if email_properties.get('html_body'):
        msg.attach(MIMEText(email_properties.pop('html_body'), 'html'))

    if email_properties.get('text_body'):
        msg.attach(MIMEText(email_properties.pop('text_body'), 'plain'))

    file = email_properties.get('file')
    file_format = email_properties.get('file_type')

    ctype = get_mimtype(file_format)
    maintype, subtype = ctype.split('/', 1)

    attach = MIMEApplication(file, Name=joined_f_name + '.' + file_format)

    # msg.add_header('Content-Disposition', 'attachment', filename="rapport." + file_format)

    msg.add_header('Content-Disposition', 'attachment')

    msg.attach(attach)

    if not msg:
        raise SMTPException("Message missing")

    return smtp_server.send(msg)


def get_mimtype(file_type=None, file_path=None):
    mime_types = {
        'pdf': 'application/pdf',
        'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    }
    if file_type:
        return mime_types.get(file_type, None)
    if file_path and type(file_path) is str:
        return mimetypes.guess_type(file_path)
    return None