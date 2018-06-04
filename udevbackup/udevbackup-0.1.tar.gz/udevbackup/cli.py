import argparse
import glob
from configparser import ConfigParser

from termcolor import cprint

from udevbackup.rule import Config, Rule


def load_config(config_dir):
    config_filenames = glob.glob('%s/*.ini' % config_dir)
    parser = ConfigParser()
    parser.read(config_filenames)
    config_section = Config.section_name
    kwargs = Config.load(parser, config_section)
    config = Config(**kwargs)
    for section in parser.sections():
        if section == config_section:
            continue
        kwargs = Rule.load(parser, section)
        rule = Rule(config, section, **kwargs)
        config.register(rule)
    return config


def main():
    """

    Returns:
      * :class:`int`: 0 in case of success, != 0 if something went wrong

    """
    parser = argparse.ArgumentParser(description='Sample command line interface')
    parser.add_argument('command', choices=('show', 'run'))
    parser.add_argument('--config-dir', '-C', default='/etc/udevbackup',
                        help='Configuration directory (default: /etc/udevbackup)')
    parser.add_argument('--no-fork', action='store_true', default=False,
                        help='do not fork before performing actions')
    args = parser.parse_args()
    return_code = 0  # 0 = success, != 0 = error
    try:
        config = load_config(args.config_dir)
    except ValueError as e:
        cprint('%s' % e, 'red')
        config = None
    if not config:
        return_code = 1
    elif args.command == 'show':
        config.show()
    elif args.command == 'run':
        config.run(fork=not args.no_fork)
    return return_code


if __name__ == '__main__':
    import doctest
    doctest.testmod()
