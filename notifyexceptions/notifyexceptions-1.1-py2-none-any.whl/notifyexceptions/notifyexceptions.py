# coding=utf-8
import sys
import traceback

from django.conf import settings
from django.core import mail


class NotifyException(object):
    """
    NotifyException can send all the traceback details to your mail.
    """

    def __init__(self):
        try:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback_details = {
                'filename': exc_traceback.tb_frame.f_code.co_filename,
                'lineno': exc_traceback.tb_lineno,
                'name': exc_traceback.tb_frame.f_code.co_name,
                'type': exc_type.__name__,
                'message': str(exc_value),
                'traceback_format': traceback.format_exc()
            }
            del (exc_type, exc_value, exc_traceback)
            html = """<!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <title>Notify Exception</title>
            </head>
            <body>
            <p>Hi,</p>
            <p>You are getting exceptions. Please find the details below:</p>
            <p>&nbsp;</p>
            <table style="height: 94px;" width="493">
            <tbody>
            <tr>
            <td style="width: 238px;">
            <pre>File Name</pre>
            </td>
            <td style="width: 239px;">{{filename}}</td>
            </tr>
            <tr>
            <td style="width: 238px;">
            <pre>Line no.</pre>
            </td>
            <td style="width: 239px;">{{lineno}}</td>
            </tr>
            <tr>
            <td style="width: 238px;">
            <pre>Name</pre>
            </td>
            <td style="width: 239px;">{{name}}</td>
            </tr>
            <tr>
            <td style="width: 238px;">
            <pre>Message</pre>
            </td>
            <td style="width: 239px;">&nbsp;{{message}}</td>
            </tr>
            <tr>
            <td style="width: 238px;">&nbsp;
            <pre>Type</pre>
            </td>
            <td style="width: 239px;">&nbsp;{{type}}</td>
            </tr>
            </tbody>
            </table>
            Traceback Format<br>
            {{traceback_format}}
            </body>
            </html>"""
            for traceback_detail in traceback_details:
                html = html.replace('{{' + str(traceback_detail) + '}}', str(traceback_details[traceback_detail]))
            if getattr(settings, 'ADMINS', False):
                mail.send_mail(getattr(settings, 'NotifyExceptionSubject', 'NotifyExceptionMail'),
                               message=html, from_email=None, recipient_list=[ADMIN[-1] for ADMIN in settings.ADMINS],
                               html_message=html, fail_silently=True)
        except Exception as e:
            print(e)
