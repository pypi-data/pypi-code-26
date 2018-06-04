import os
import platform
import pwd
import shlex
import smtplib
import subprocess
import sys
import time
from collections import OrderedDict
from configparser import ConfigParser
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from getpass import getuser
from logging import ERROR, INFO, WARNING
from tempfile import NamedTemporaryFile, mkdtemp, gettempdir
from typing import Union

from google_speech import Speech
from termcolor import cprint


class Section:
    text_options = set()
    bool_options = set()
    int_options = set()
    float_options = set()
    required = set()

    @classmethod
    def load(cls, parser: ConfigParser, section: str):
        kwargs = {}
        if parser.has_section(section):
            for option in parser.options(section):
                if option in cls.text_options:
                    kwargs[option] = parser.get(section, option)
                elif option in cls.bool_options:
                    kwargs[option] = parser.getboolean(section, option)
                elif option in cls.int_options:
                    kwargs[option] = parser.getint(section, option)
                elif option in cls.float_options:
                    kwargs[option] = parser.getfloat(section, option)
                else:
                    cprint('  valid text options: %s' % ', '.join(cls.text_options), 'yellow')
                    cprint('  valid bool options: %s' % ', '.join(cls.bool_options), 'yellow')
                    cprint('  valid int options: %s' % ', '.join(cls.int_options), 'yellow')
                    cprint('  valid float options: %s' % ', '.join(cls.float_options), 'yellow')
                    raise ValueError('Unrecognized option [%s] %s' % (section, option))
        for required_option in cls.required:
            if required_option in kwargs:
                continue
            raise ValueError('option %s is required in section %s' % (required_option, section))
        return kwargs


class Rule(Section):
    text_options = {'fs_uuid', 'command', 'script', 'stdout', 'stderr', 'mount_options', 'user',
                    'pre_script', 'post_script'}
    required = {'fs_uuid', 'script'}

    def __init__(self, config, name, fs_uuid: str, script: str, command: str = 'bash', user: str=getuser(),
                 stdout: str = '%(tmp)s/%(name)s.out', stderr: str = '%(tmp)s/%(name)s.err', mount_options: str='',
                 pre_script: Union[str, None]=None, post_script: Union[str, None]=None,
                 ):
        self.config = config
        self.name = name
        self.errors = []
        self.fs_uuid = fs_uuid
        self.script = script
        self.pre_script = pre_script
        self.post_script = post_script
        self.command = shlex.split(command)
        self.user = user
        self.mount_options = shlex.split(mount_options)
        self.stdout = stdout % {'name': self.name, 'tmp': gettempdir()}
        self.stderr = stderr % {'name': self.name, 'tmp': gettempdir()}
        self._is_mounted = False
        self._mount_dir = None
        self._stdout_fd = None
        self._stderr_fd = None

    def execute(self):
        self.set_up()
        if self._is_mounted:
            self.backup()
        self.tear_down()

    def set_up(self):
        self._stdout_fd = open(self.stdout, 'wb')
        self._stderr_fd = open(self.stdout, 'wb')
        if not self.execute_script('pre_script', cwd=None):
            return False
        self._mount_dir = mkdtemp(prefix='%s-' % self.fs_uuid)
        uid = pwd.getpwnam(self.user).pw_uid
        gid = pwd.getpwnam(self.user).pw_gid
        try:
            os.chown(self._mount_dir, uid=uid, gid=gid)
        except PermissionError:
            self.errors.append('Unable to chown mount folder to %(user)s' % self.__dict__)
            return False
        cmd = ['mount'] + self.mount_options + ['UUID=%s' % self.fs_uuid, self._mount_dir]
        p = subprocess.Popen(cmd, stderr=self._stderr_fd, stdout=self._stdout_fd)
        p.communicate()
        if p.returncode != 0:
            self.errors.append('Unable to mount the device %(fs_uuid)s' % self.__dict__)
            return False
        self._is_mounted = True
        return True

    def run(self):
        self.set_up()
        if not self.errors:
            self.backup()
        self.tear_down()

    def backup(self) -> bool:
        return self.execute_script('script', cwd=self._mount_dir)

    def execute_script(self, script_attr_name, cwd=None):
        script_content = getattr(self, script_attr_name)
        if not script_content:
            return True
        with NamedTemporaryFile() as fd:
            fd.write(script_content.encode())
            fd.flush()
            command = ['sudo', '-Hu', self.user] + self.command + [fd.name]
            p = subprocess.Popen(command, cwd=cwd, stderr=self._stderr_fd, stdout=self._stdout_fd)
            p.communicate()
            if p.returncode != 0:
                self.errors.append('Unable to execute script %(cmd)s' % {'cmd': script_attr_name})
                return False
            return True

    def tear_down(self):
        if self._is_mounted:
            p = subprocess.Popen(['umount', self._mount_dir], stderr=self._stderr_fd, stdout=self._stdout_fd)
            p.communicate()
            if p.returncode != 0:
                self.errors.append('Unable to umount %(fs_uuid)s' % self.__dict__)
            else:
                self._is_mounted = False
        if self._mount_dir:
            os.rmdir(self._mount_dir)
            self._mount_dir = None
        self.execute_script('post_script', cwd=None)
        if self._stderr_fd:
            self._stderr_fd.close()
        if self._stdout_fd:
            self._stdout_fd.close()


class Config(Section):
    section_name = 'main'
    lang = 'en'
    text_options = {'smtp_auth_user', 'smtp_auth_password', 'smtp_server', 'smtp_from_email', 'smtp_to_email'}
    bool_options = {'use_speech', 'use_stdout', 'use_smtp', 'smtp_use_tls', 'smtp_use_starttls'}
    int_options = {'smtp_smtp_port'}
    udev_rule_filename = '/etc/udev/rules.d/'

    def __init__(self, smtp_auth_user: Union[str, None] = None, smtp_auth_password: Union[str, None] = None,
                 smtp_server: str = 'localhost', smtp_smtp_port: int=25,
                 smtp_use_tls: bool=False, smtp_use_starttls: bool=False, smtp_to_email: Union[str, None]=None,
                 smtp_from_email: Union[str, None] = None, use_speech: bool = False,
                 use_stdout: bool = False, use_smtp: bool = False):
        self.smtp_auth_user = smtp_auth_user
        self.smtp_auth_password = smtp_auth_password
        self.smtp_server = smtp_server
        self.smtp_smtp_port = smtp_smtp_port
        self.smtp_use_tls = smtp_use_tls
        self.smtp_use_starttls = smtp_use_starttls
        self.smtp_from_email = smtp_from_email or 'root@%s' % (platform.node())
        self.smtp_to_email = smtp_to_email
        self.use_speech = use_speech
        self.use_stdout = use_stdout
        self.use_smtp = use_smtp
        self.rules = OrderedDict()  # rules[fs_uuid] = Rule()
        self._log_content = ''

    def register(self, rule: Rule):
        self.rules[rule.fs_uuid] = rule

    def run(self, fork=True):
        new_fs_uuid = os.environ.get('ID_FS_UUID', '')
        if new_fs_uuid not in self.rules:
            return
        rule = self.rules[new_fs_uuid]
        if fork and not self.fork():
            return
        self.log_text('Device is connected.', level=INFO)
        rule.run()
        if rule.errors:
            self.log_text('An error happened.', level=ERROR)
            for error in rule.errors:
                self.log_text(error, level=ERROR)
        else:
            self.log_text('Successful.', level=INFO)

        while os.path.exists('/dev/disk/by-uuid/%s' % rule.fs_uuid):
            self.log_text('Please disconnect the device.', level=INFO)
            time.sleep(15)
        if self.use_smtp:
            subject = '%s' % rule.name
            if rule.errors:
                subject += ' [KO]'
            else:
                subject += ' [OK]'
            self.send_email(self._log_content, subject=subject, attachments=[rule.stdout, rule.stderr])

    def log_text(self, text, level=INFO):
        if self.use_speech:
            try:
                Speech(text, self.lang).play([])
            except KeyboardInterrupt:
                cprint(text, 'red')
        if self.use_stdout:
            color = 'green'
            if level >= WARNING:
                color = 'yellow'
            if level >= ERROR:
                color = 'red'
            cprint(text, color)
        self._log_content += text
        self._log_content += '\n'

    @staticmethod
    def fork():
        wpid = os.fork()
        if wpid != 0:
            return False
        wpid = os.fork()
        if wpid != 0:
            return False
        sys.stdout.flush()
        sys.stderr.flush()
        sys.stdout = open('/dev/null', 'w')
        sys.stderr = open('/dev/null', 'w')
        sys.stdin = open('/dev/null', 'r')
        return True

    def show(self):
        cmd = 'ACTION=="add", ENV{DEVTYPE}=="partition", RUN+="%s"' % sys.argv[0]
        if not os.path.isfile(self.udev_rule_filename):
            cprint('please run the following commands: ', 'yellow')
            cprint('echo \'%s\' | sudo tee %s' % (cmd, self.udev_rule_filename))
            cprint('udevadm control --reload-rules')
        for rule in self.rules.values():
            cprint('[%s]' % rule.name, 'yellow')
            cprint('file system uuid: %s' % rule.fs_uuid, 'green')
            cprint('extra mount options: %s' % ' '.join(rule.mount_options), 'green')
            cprint('mounted file system will be chowned to: %s' % rule.user, 'green')
            cprint('stdout will be written to: %s' % rule.stdout, 'green')
            cprint('stderr will be written to: %s' % rule.stderr, 'green')
            cprint('command to execute: ', 'green')
            cmd = ' '.join(shlex.quote(x) for x in rule.command)
            cprint('MOUNT_POINT=[mount point]')
            cprint('cat << EOF > [tmpfile] ; sudo -Hu %s %s [tmpfile]\n%s\nEOF' % (rule.user, cmd, rule.script))
        if not self.rules:
            cprint('Please create a .ini file in the config dir', 'red')

    def send_email(self, content, subject=None, attachments=None):
        try:
            if self.smtp_use_tls:
                smtp = smtplib.SMTP_SSL(self.smtp_server, self.smtp_smtp_port)
                smtp.set_debuglevel(0)
            else:
                smtp = smtplib.SMTP(self.smtp_server, self.smtp_smtp_port)
                smtp.set_debuglevel(0)
                smtp.starttls()
            if self.smtp_auth_user and self.smtp_auth_password:
                smtp.login(self.smtp_auth_user, self.smtp_auth_password)
            if not self.smtp_from_email or not self.smtp_to_email:
                return
            msg = MIMEMultipart()
            msg['From'] = self.smtp_from_email
            msg['To'] = self.smtp_to_email
            if subject:
                msg['Subject'] = subject
            msg.attach(MIMEText(content, 'plain'))
            if attachments:
                for attachment in attachments:
                    if not os.path.isfile(attachment):
                        continue
                    part = MIMEBase('application', 'octet-stream')
                    with open(attachment, 'rb') as fd:
                        attachment_content = fd.read()
                    part.set_payload(attachment_content)
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition', "attachment; filename= %s" % os.path.basename(attachment))
                    msg.attach(part)

            smtp.sendmail(self.smtp_from_email, [self.smtp_to_email], msg.as_string())
        except Exception as e:
            pass
