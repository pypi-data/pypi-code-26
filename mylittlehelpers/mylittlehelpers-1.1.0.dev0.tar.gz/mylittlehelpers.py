import getpass
import json
import time
import smtplib
from math import trunc
import sys
import os
import logging
from io import BytesIO
import ntpath
import configparser
import boto3


class ImproperlyConfigured(BaseException):
    pass


def __except__(exception, replacement_function):
    """
    Function wrapper. If the wrapped function encounters the specified exception, it will instead perform the replacement function (with the same arguments).
    
    :param exception: (Exception) 
    :param replacement_function: 
    :return: 
    """
    def _try_wrap(function):
        def __try_wrap(*__args, **__kwargs):
            try:
                return function(*__args, **__kwargs)
            except exception as e:
                return replacement_function(*__args, **__kwargs)
        return __try_wrap
    return _try_wrap


def time_check(start):
    current_time = time.time()
    auto_refresh = False
    hours, rem = divmod(current_time - start, 3600)
    minutes, seconds = divmod(rem, 60)
    if minutes > 7:
        start = time.time()
        auto_refresh = True

    return start, auto_refresh


def time_elapsed(start, string_width=12):
    """
    Returns time elapsed in "HH:MM:SS" format.

    :param start: (int, float) unix epoch
    :param string_width: (int) width of returned string
    :return: (str) time elapsed since start in "HH:MM:SS" format
    """
    current_time = time.time()
    hours, rem = divmod(current_time - start, 3600)
    minutes, seconds = divmod(rem, 60)
    time_string = f'{trunc(hours):02d}:{trunc(minutes):02d}:{trunc(seconds):02d}'
    return f'{time_string:>{string_width}}'


def time_bomb(countdown, package=(print, ("BOOM",)), action="", dots=3):
    """
    tells the user that {action} will be done in {countdown} seconds. package[0] is the function and package[1] is package[0] is a list of arguments to be passed to package[0]

    :param countdown: (int) time until package[0] is called
    :param package: (list, tuple) package[0] is a function object, package[1] is a tuple or list of arguments to be passed to package[0]
    :param action: (str) description of what the package will do
    :param dots: (int) number of dots between counts
    :return:
    """
    action = action if action else package[0].__name__
    sys.stdout.write(f"{action} in {countdown}")
    sys.stdout.flush()
    for i in range(countdown - 1, -1, -1):
        for j in range(dots):
            time.sleep(1.0/(dots + 1))
            sys.stdout.write(".")
            sys.stdout.flush()
        time.sleep(.25)
        sys.stdout.write(str(i))
        sys.stdout.flush()
    print("")
    package[0](*package[1])

def setup_logger(name, log_file, level=logging.INFO):
    """
    sets up a file logger with log level INFO

    :param name: (str) name of logger
    :param log_file: (str) path to log file location
    :param level: (logging.level)
    :return: (logging.logger)
    """
    try:
        os.makedirs(os.path.dirname(log_file))
    except FileExistsError:
        pass

    handler = logging.FileHandler(log_file)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger

def remove_if_exists(file_name):
    """
    removes file located at specified path of it exists, otherwise does nothing.

    :param file_name: (str) path to file
    :return:
    """
    try:
        os.remove(file_name)
    except OSError:
        pass


def send_gmail(recipient, subject, body, user=None, pwd=None):
    """
    sends an email to the specified recipient(s)

    :param recipient: (str, list) recipient email address(es)
    :param subject: (str) subject line
    :param body: (str) email body
    :param user: (str) sender email address
    :param pwd: (str) sender password
    :return:
    """
    gmail_user = user
    gmail_pwd = pwd
    FROM = user
    TO = recipient if type(recipient) is list else [recipient]
    SUBJECT = subject
    TEXT = body

    # Prepare actual message
    message = """From: %s\nTo: %s\nSubject: %s\n\n%s
    """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(gmail_user, gmail_pwd)
        server.sendmail(FROM, TO, message)
        server.close()
        print('Email Sent.')
    except:
        print("failed to send mail")


class SendError(BaseException):
    pass


def binary(file_path):
    """
    Read specified file as binary and return its name and the binary contents

    :param file_path: (str) path to file
    :return:
    """
    with open(file_path, 'rb') as binary_chunk:
        return ntpath.basename(file_path), binary_chunk.read()


def get_credentials(path, region="microsoft_exchange_email", address_key="email", password_key="email_password"):
    """
    return email address and password from specified region and keys

    :param path: (str) path to config file
    :param region: (str) region containing email credentials
    :param address_key: (str) key containing email address in region
    :param password_key: (str) key containing email password in region
    :return: (dict) with keys email_address and email_password
    """
    config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
    config.read(path)
    credentials = {"email_address": config.get(region, address_key), "email_password": config.get(region, password_key)}
    return credentials


def send_ses(access_id, access_key, sender, recipient_list, subject, body_html, body_text=None):
    from botocore.exceptions import ClientError

    AWS_REGION = "us-east-1"

    CHARSET = "UTF-8"

    client = boto3.client('ses',
                          aws_access_key_id=access_id,
                          aws_secret_access_key=access_key,
                          region_name=AWS_REGION)

    try:
        response = client.send_email(
            Destination={
                'ToAddresses': recipient_list
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': body_html,
                    },
                    'Text': {
                        'Charset': CHARSET,
                        'Data': body_text,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': subject,
                },
            },
            Source=sender,
        )
    # Display an error if something goes wrong.
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['ResponseMetadata']['RequestId'])