import os
import ConfigParser


CONFIG_FILE = 'rgb_api.conf'


class RGB_ConfigError(Exception):
    '''Config error base class'''
    pass


def get_config():
    config = None
    
    # /currentdir/rgb_api.conf, /home/username/rgb_api.conf, /etc/rgb_api.conf
    base_dir = '.' if __name__ == '__main__' else os.path.dirname(__file__)
    config_paths = [os.path.join(os.path.abspath(base_dir), CONFIG_FILE),
                    os.path.expanduser('~/{}'.format(CONFIG_FILE)),
                    '/etc/{}'.format(CONFIG_FILE)]

    parser = ConfigParser.SafeConfigParser()
    config = parser.read(config_paths)
    if not config:
        raise RGB_ConfigError('config file not found. ' \
                              'Searched %s' % (config_paths))
    return parser
