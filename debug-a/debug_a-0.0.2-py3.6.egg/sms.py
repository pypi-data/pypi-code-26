# -*- coding: utf-8 -*-


from retrying import retry
import requests
import os

"""
——————————————————————————————————————————————————————————————————————————————————————————
微信推送
——————————————————————————————————————————————————————————————————————————————————————————
"""

@retry(stop_max_attempt_number=6)
def push_sms(title, content, key):
    """使用server酱推送消息到微信"""
    url = 'https://sc.ftqq.com/%s.send' % key
    requests.post(url, data={'text': title, 'desp': content})


"""
—————————————————————————————————————————————————————————————————————
邮件发送模块，支持发送附件
——————————————————————————————————————————————————————————————————————
"""

import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class EmailSender:
    """
    example
    ----------------
    subject = '附件发送测试'
    content = '检测附件发送是否成功'
    files = ['test.py',
             'f:\\已下载.txt']

    e = EmailSender('zeng_bin8888@163.com', pw=pw, service='163')
    e.send_email(to, subject, content, files)
    """
    def __init__(self, from_, pw, service='163'):
        self.from_ = from_  # 用于发送email的邮箱
        self.pw = pw        # 发送email的邮箱密码

        # 登录邮箱
        self.smtp = smtplib.SMTP()
        smtps = {
            "qq": 'smtp.exmail.qq.com',
            "163": 'smtp.163.com'
        }
        assert service in smtps.keys(), "目前仅支持：%s" % str(smtps.keys()).strip("dict_keys()")
        smtp = smtps[service]
        self.smtp.connect(smtp)
        self.smtp.login(self.from_, self.pw)


    def construct_msg(self, to, subject, content, files=None):
        """构造email信息

        parameters
        ---------------
        subject     邮件主题
        content     邮件文本内容
        files       附件（list）,可以是相对路径下的文件，也可以是绝对路径下的文件

        return
        --------------
        msg         构造好的邮件信息
        """
        msg = MIMEMultipart()
        msg['from'] = self.from_
        msg['to'] = to
        msg['subject'] = subject
        txt = MIMEText(content)
        msg.attach(txt)

        # 添加附件
        if files is not None:
            for file in files:
                f = MIMEApplication(open(file, 'rb').read())
                f.add_header('Content-Disposition', 'attachment',
                             filename=os.path.split(file)[-1])
                msg.attach(f)

        return msg


    @retry(stop_max_attempt_number=6)
    def send_email(self, to, subject, content, files=None):
        """登录邮箱，发送msg到指定联系人"""
        smtp = self.smtp
        msg = EmailSender.construct_msg(self, to, subject, content, files=files)
        smtp.sendmail(self.from_, to, str(msg))


    def quit(self):
        smtp = self.smtp
        smtp.quit()  # 退出登录


def send_email(from_, pw, to, subject, content, files=None, service='163'):
    """邮件发送（支持附件），推荐使用163邮箱"""
    se = EmailSender(from_=from_, pw=pw, service=service)
    se.send_email(to=to, subject=subject, content=content, files=files)
    se.quit()
