import json
import smtplib
import threading
import socket

from racengine.exceptions import SMTPException


class SmtpServer(object):
    def __init__(self, host='localhost', port=25, username='', password='', fileconf=None, local_hostname=None):
        conf = {}
        self.use_tls = False
        self.use_ssl = False
        self.connection = None

        if fileconf:
            with open(fileconf, 'r') as f:
                conf = json.loads(f.read())
        self.host = conf.get('host', None) or host
        self.port = conf.get('port', None) or port
        self.username = conf.get('username', None) or username
        self.password = conf.get('password', None) or password
        self.port = port

        if port == 587:
            self.use_tls = True
        elif port == 465:
            self.use_ssl = True

        self.local_hostname = local_hostname
        self._lock = threading.RLock()

    def open(self):
        """
        Ensures we have a connection to the email server. Returns whether or
        not a new connection was required (True or False).
        """
        if self.connection:
            # Nothing to do if the connection is already open.
            return False
        try:
            if self.use_ssl:
                self.connection = smtplib.SMTP_SSL(self.host, self.port, local_hostname=self.local_hostname)
            else:
                self.connection = smtplib.SMTP(self.host, self.port, local_hostname=self.local_hostname)
            if self.use_tls:
                self.connection.ehlo()
                self.connection.starttls()
                self.connection.ehlo()
            if self.username and self.password:
                self.connection.login(self.username, self.password)
            return True
        except:
                raise

    def close(self):
        """Closes the connection to the email server."""
        try:
            try:
                self.connection.quit()
            except socket.sslerror:
                # This happens when calling quit() on a TLS connection
                # sometimes.
                self.connection.close()
            except:
                raise
        finally:
            self.connection = None

    def send(self, msg, emails=None, title='', subject='', attachment=''):
        # if emails is None and msg.get('To', None) is None:
        #     return False

        if not msg:
            return
        self._lock.acquire()
        try:
            new_conn_created = self.open()
            if not self.connection:
                # We failed silently on open().
                # Trying to send would be pointless.
                return False

            self.connection.sendmail(msg.get('From'), msg.get('To'), msg.as_string())

            if new_conn_created:
                self.close()
        except:
            raise
        finally:
            self._lock.release()

        return True
