import re

from cloudshell.cli.command_template.command_template import CommandTemplate


COPY = CommandTemplate(
    'copy {src} {dst}',
    action_map={
        r'[Uu]ser': lambda session, logger: session.send_line('', logger),
        r'[Pp]assword': lambda session, logger: session.send_line('', logger),
        r'for later use\?\[yes/no\]': lambda session, logger: session.send_line('no', logger),
        r'overwrite .* \([Nn]/[Yy]\)': lambda session, logger: session.send_line('y', logger),
    },
    error_map={
        r'^((?!File copied successfully).)*$': 'Fail to copy a file',
    }
)

SHOW_VERSION = CommandTemplate('show version')

UPGRADE = CommandTemplate(
    'upgrade hd {location} {src_path} reboot-after-upgrade',
    action_map={
        re.escape('System configuration has been modified. Save? [yes/no]:'):
            lambda session, logger: session.send_line('no', logger),
    },
    error_map={
        r'Upgrade failed': 'Failed to load firmware',
        r'Failed to get file from ftp server': 'Failed to load firmware',
    }
)
