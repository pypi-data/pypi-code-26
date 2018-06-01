#!/usr/bin/env python
import socket
from pubsub import pub
from blogengine2.contrib.api_v1.email import send_mail_wrapper
def get_from_addr():
    if socket.gethostname() == 'isotopesoftware.ca':
        from_addr = 'erob@isotopesoftware.ca'
    else:
        from_addr = 'erob@localhost'
    return from_addr

def new_vote_callback(path_url):
    """
    Error callback to send a mail when a new HTTP request returns an error
    code (400, 404, 500, etc)
    """
    

    #msg = """
    #{error_type}: {location}
    #IP: {ip}
    #""".format(
    #    error_type=error_type,
    #    location=path_info,
    #    #referer=referer,
    #    ip=remote_ip)
    msg = "New vote saved at %s" % path_url

    recipients = ('erob@localhost',)
    send_mail_wrapper(recipients, 
        from_addr=get_from_addr(), 
        subject='New vote saved', 
        message=msg)

pub.subscribe(new_vote_callback, 'new_vote_callback')

