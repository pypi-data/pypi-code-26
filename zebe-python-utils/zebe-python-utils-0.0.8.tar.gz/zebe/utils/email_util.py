# -*- coding: utf-8 -*-
"""
    zebe.util.email_util
    ~~~~~~~~~~~~~~~~

    邮件工具类

    :copyright: (c) 2018 by Zebe.
    :license: BSD, see LICENSE for more details.
"""

import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr


def send_html_mail(subject, content, host, port, password, sender, receiver):
    """
    发送HTML邮件
    :param subject: 主体
    :param content: HTML内容
    :param host: 邮箱主机
    :param port: 邮箱端口
    :param password: 发信人密码
    :param sender: 发信人邮箱
    :param sender_show_name: 发信人显示名称
    :param receiver: 接收者，可以是list
    """
    send_html_mail_with_nickname(subject, content, host, port, password, sender, '', receiver)


def send_html_mail_with_nickname(subject, content, host, port, password, sender, sender_show_name, receiver):
    """
    发送HTML邮件
    :param subject: 主体
    :param content: HTML内容
    :param host: 邮箱主机
    :param port: 邮箱端口
    :param password: 发信人密码
    :param sender: 发信人邮箱
    :param sender_show_name: 发信人显示名称
    :param receiver: 接收者，可以是list
    """
    msg = MIMEText(content, _subtype='html', _charset='utf-8')
    msg['Subject'] = subject
    if len(sender_show_name) > 0:
        msg['From'] = formataddr([sender_show_name, sender])
    else:
        msg['From'] = sender
    s = smtplib.SMTP_SSL(host, port)
    s.login(sender, password)
    receiver_emails = []
    if isinstance(receiver, str):
        array = receiver.split(",")
        for email in array:
            receiver_emails.append(email)
    elif isinstance(receiver, list):
        receiver_emails = receiver
    s.sendmail(sender, receiver_emails, msg.as_string())
