# -*- coding: utf-8 -*-
"""
    okuyama.client
    ~~~~~~~~~~~~~~

    Python client for Distributed KVS okuyama.


    :copyright: (c) 2014-2015 Kobe Digitallabo, Inc, All rights reserved.
    :copyright: (c) 2014-2015 Shinya Ohyanagi, All rights reserved.
    :license: BSD, see LICENSE for more details.
"""
import sys
import re
import socket
import logging
import argparse
import random
from base64 import b64encode, b64decode

__version__ = '0.0.1'


PY2 = sys.version_info[0] == 2
HOST_PATTERN = re.compile('^[a-zA-Z\d\.\-\_]+[:][0-9]+$', re.IGNORECASE)

"""Copied from `werkzuig._compat.py`.

see https://github.com/mitsuhiko/werkzeug/blob/master/werkzeug/_compat.py
"""
if PY2:
    text_type = unicode  # noqa F821

    iterkeys = lambda d: d.iterkeys()  # noqa E731
    itervalues = lambda d: d.itervalues()  # noqa E731
    iteritems = lambda d: d.iteritems()  # noqa E731

    def to_bytes(x, charset=sys.getdefaultencoding(), errors='strict'):
        if x is None:
            return None
        if isinstance(x, (bytes, bytearray, buffer)):  # noqa F821
            return bytes(x)
        if isinstance(x, unicode):  # noqa F821
            return x.encode(charset, errors)
        raise TypeError('Expected bytes')
else:
    text_type = str

    iterkeys = lambda d: iter(d.keys())  # noqa E731
    itervalues = lambda d: iter(d.values())  # noqa E731
    iteritems = lambda d: iter(d.items())  # noqa E731

    def to_bytes(x, charset=sys.getdefaultencoding(), errors='strict'):
        if x is None:
            return None
        if isinstance(x, (bytes, bytearray, memoryview)):
            return bytes(x)
        if isinstance(x, str):
            return x.encode(charset, errors)
        raise TypeError('Expected bytes')


def to_unicode(x, charset=sys.getdefaultencoding(), errors='strict', allow_none_charset=False):
    """Copied from `werkzuig._compat.py`.

    see https://github.com/mitsuhiko/werkzeug/blob/master/werkzeug/_compat.py
    """
    if x is None:
        return None
    if not isinstance(x, bytes):
        return text_type(x)
    if charset is None and allow_none_charset:
        return x
    return x.decode(charset, errors)


class CommandInterface(object):
    """ Interface of okuyama command. """
    def __init__(self, constants, logger):
        """Interface of command.

        :param constants: okuyama constants
        :param logger: :class:`logging`
        """
        self.constants = constants
        self.logger = logger
        self.id = None

    def command_id(self):
        """ Command id. """
        pass

    def build(self, **kwargs):
        """Build command.

        :param **kwargs:
        """
        raise NotImplementedError()

    def parse(self, **kwargs):
        """Prase response

        :param **kwargs:
        """
        raise NotImplementedError()

    def _parse(self, data, id):
        """Parse response from okuyama.

        :param data: okuyama raw data
        :param id: Process id
        """
        responses = to_unicode(data).split(self.constants.DATA_DELIMITER)
        if responses[0] == id:
            return responses

        self.logger.error(responses)
        raise OkuyamaError('Response receve wrong id data.')

    def send(self, socket, command):
        """Send command to okuyama.

        :param socket: :class: 'socket`
        :param command: okuyama command
        """
        if socket is None:
            raise OkuyamaError('Connection refused.')

        try:
            self.logger.debug(to_unicode(command).replace('\n', '\\n'))

            socket.send(to_bytes(command))

            ret = ''
            while True:
                buf = socket.recv(4096)
                ret += buf
                if '\n' in buf:
                    break

            self.logger.debug(to_unicode(ret).replace('\n', '\\n'))

            return to_unicode(ret)
        except Exception as e:
            self.logger.error(e)


class GetCommand(CommandInterface):
    """ okuyama get command. """
    def command_id(self):
        """ Command id. """
        self.id = self.constants.ID_GET

    def build(self, **kwargs):
        """Build Get command.

        :param **kwargs:
        """
        key = kwargs['key']
        mode = self.id if self.id is not None else self.constants.ID_GET

        command = '{0}{1}{2}\n'.format(
            mode,
            self.constants.DATA_DELIMITER,
            to_unicode(b64encode(to_bytes(key))),
        )
        self.logger.debug(command)

        return command

    def parse(self, response):
        """Parse okuyama response.

        :param response: okuyama response string.
        """
        mode = self.id if self.id is not None else self.constants.ID_GET
        responses = self._parse(response, mode)
        result = responses[1]
        if result == 'true':
            if responses[2] == self.constants.BLANK_STRING:
                return ''
            else:
                return b64decode(responses[2])

            if mode == Constants.ID_GETS:
                return responses[3]

        elif result == 'false':
            self.logger.error('Get returns false.')
            return False
        elif result == 'error':
            self.logger.error('Get returns error.')
            return None


class SetCommand(CommandInterface):
    """ okuyama set command. """

    def command_id(self):
        """ Command id. """
        self.id = self.constants.ID_SET

    def build(self, **kwargs):
        """Build okuyama command.

        :param **kwargs:
        """
        value = kwargs['value']
        key = kwargs['key']
        tags = kwargs['tags'] if 'tags' in kwargs else None
        version = kwargs['version'] if 'version' in kwargs else None
        mode = self.id if self.id is not None else self.constants.ID_SET

        if value is None or value == '':
            value = self.constants.BLANK_STRING

        value = to_unicode(b64encode(to_bytes(value)))

        command = '{0}{1}{2}{3}'.format(
            mode, self.constants.DATA_DELIMITER,
            to_unicode(b64encode(to_bytes(key))),
            self.constants.DATA_DELIMITER,
        )

        if tags is None:
            command += self.constants.BLANK_STRING
        elif isinstance(tags, list):
            buffers = []
            for tag in tags:
                buffers.append(to_unicode(b64encode(to_bytes(tag))))
            command += self.constants.TAG_DELIMITER.join(buffers)
        else:
            command += to_unicode(b64encode(to_bytes(tags)))

        command += self.constants.DATA_DELIMITER \
            + self.constants.TRANSACTION_CODE \
            + self.constants.DATA_DELIMITER + value

        if mode == self.constants.ID_CAS \
                and version is not None \
                and isinstance(version, int):
            command += self.constants.DATA_DELIMITER + version

        command += '\n'

        self.logger.debug('Set command:' + command)

        return command

    def parse(self, response):
        """Parse data okuyama response.

        :param response: okuyama response
        """
        mode = self.id if self.id is not None else self.constants.ID_SET
        responses = self._parse(response, mode)
        if responses[1] == 'true':
            return True
        elif responses[1] == 'false':
            return False


class DeleteCommand(CommandInterface):
    """ okuyama delete command.  """
    def command_id(self):
        """ Command id. """
        self.id = self.constants.ID_REMOVE

    def build(self, **kwargs):
        """Build delete command.

        :param **kwargs:
        """
        key = kwargs['key']
        if key == '' or key is None:
            return False

        mode = self.id if self.id is not None else self.constants.ID_REMOVE
        key = to_unicode(b64encode(to_bytes(key)))
        command = '{0}{1}{2}{3}{4}\n'.format(
            mode,
            self.constants.DATA_DELIMITER,
            key,
            self.constants.DATA_DELIMITER,
            self.constants.TRANSACTION_CODE,
        )
        return command

    def parse(self, response):
        """Prase okuyama response.

        :param response:
        """
        mode = self.id if self.id is not None else self.constants.ID_REMOVE
        responses = self._parse(response, mode)
        if responses[1] == 'true':
            return True

        return False


class GetKeysByTagCommand(CommandInterface):

    def command_id(self):
        """ Command id. """
        self.id = self.constants.ID_TAG_SET

    def build(self, **kwargs):
        """Build Get keys by tag command.

        :param **kwargs:
        """
        tag = kwargs['tag']
        returns = 'false'
        if 'returns' in kwargs and kwargs['returns'] == 'true':
            returns = 'true'

        mode = self.id if self.id is not None else self.constants.ID_TAG_SET

        command = mode + self.constants.DATA_DELIMITER \
            + to_unicode(b64encode(to_bytes(tag))) \
            + self.constants.DATA_DELIMITER
        command += returns + '\n'

        return command

    def parse(self, response):
        """Parse okuyama response.

        :param response:
        """
        mode = self.constants.ID_TAG_GET
        responses = self._parse(response, mode)
        if responses[1] == 'true':
            data = responses[2]
            if data == self.constants.BLANK_STRING:
                return None
            tags = data.split(self.constants.TAG_DELIMITER)
            ret = [b64decode(r) for r in tags]

            return ret


class Constants(object):

    """
    okuyama constants
    """
    #: Data delimiter.
    DATA_DELIMITER = ','

    #: Tag delimiter.
    TAG_DELIMITER = ':'

    #: Byte data delimiter
    BYTE_DATA_DELIMITER = ':#:'

    #: Alternative blank string.
    BLANK_STRING = '(B)'

    #: Transaction code.
    TRANSACTION_CODE = '0'

    #: Initialize okuyama.
    ID_INIT = '0'

    #: Set data.
    ID_SET = '1'

    #: Get data.
    ID_GET = '2'

    #: Set tag data.
    ID_TAG_SET = '3'

    #:  Get tag data.
    ID_TAG_GET = '4'

    #: Remove data.
    ID_REMOVE = '5'

    #: Add data(not override).
    ID_ADD = '6'

    #: Play script.
    ID_PLAY_SCRIPT = '8'

    #: Play script for update.
    ID_UPDATE_SCRIPT = '9'

    #: Gets.
    ID_GETS = '15'

    #: Cas.
    ID_CAS = '16'

    #: Max data size to save.
    MAX_SIXE = 2560

    #: Binary data per size.
    BINARY_SIZE = 2560


class OkuyamaError(Exception):
    """ Okuyama Exception class. """
    pass


class Client(object):
    #: Default log format.
    debug_log_format = (
        '[%(asctime)s %(levelname)s][%(pathname)s:%(lineno)d]: %(message)s'
    )

    #: okuyama constants.
    constants = Constants

    #: okuyama commands.
    commands = {}

    def __init__(self, logger=None, constants=None):
        """Construct a client.

        :param logger: :class:`logging`
        """
        self.socket = None
        if logger is None:
            logging.basicConfig(level=logging.INFO, format=self.debug_log_format)
            logger = logging.getLogger('okuyama')

        self.logger = logger

        if constants is not None:
            self.constants = constants

        #: Default commands.
        self.register_command('get', GetCommand)
        self.register_command('set', SetCommand)
        self.register_command('delete', DeleteCommand)
        self.register_command('get_keys_by_tag', GetKeysByTagCommand)

    def register_command(self, name, command_class):
        """Register okuyama command.

        :param name: Command name
        :param command_class: okuyama command class
        """
        c = command_class(self.constants, self.logger)
        if not isinstance(c, CommandInterface):
            raise OkuyamaError('Command is not instance of OkuyamaInterface.')

        c.command_id()
        self.commands[name] = c

    def connect(self, address):
        """Connect to okuyama.

        :param address: okuyama MasterNode Address
        """
        host, port = address.split(':')
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ret = None
        try:
            sock.connect((host, int(port)))
            ret = sock
        except Exception as e:
            self.logger.error(e)

        return ret

    def auto_connect(self, addresses):
        """Connect to okuyama.

        :param address: okuyama MasterNode Addresses
        """
        if isinstance(addresses, list):
            #: Access to MasterNode by random.
            random.shuffle(addresses)
        elif isinstance(addresses, str):
            address = [addresses]
        elif isinstance(addresses, unicode):  # noqa F821
            address = [addresses]

        sock = None
        for address in addresses:
            #: address should be `HOST:PORT`.
            if validate_host_format(address) is False:
                continue

            self.logger.info('Connecting to %s', address)
            sock = self.connect(address)
            if sock is not None:
                self.socket = sock
                break

        if sock is None:
            raise OkuyamaError('{0}, Connection refused.'.format(address))

    def is_connected(self):
        """ Connected to okuyama? """
        if self.socket is not None:
            return True

        return False

    def close(self):
        """ Close connection. """
        if self.is_connected() is True:
            self.socket.close()
            self.socket = None

    def execute(self, command_name, **kwargs):
        """Execute command.

        :param command_name: Command name.
        :param **kwargs: Command kwargs
        """
        c = self.commands[command_name]
        command = c.build(**kwargs)
        ret = c.send(self.socket, command)
        response = c.parse(ret)

        return response

    def set(self, key, value, tags=None, version=None):
        """Set data to okuyama.

        Alias of execute('set')

        :param key: Key
        :param value: Value
        """
        response = self.execute('set', key=key, value=value, tags=tags, version=version)

        return response

    def get(self, key):
        """Get data from okuyama.

        Alias of execute('get')

        :param key: Key
        """
        response = self.execute('get', key=key)

        return response

    def delete(self, key):
        """Delete data from okuyama.

        Alias of execute('delete')

        :param key:
        """
        response = self.execute('delete', key=key)

        return response


def validate_host_format(address):
    """ Validate host name format.

    :param address: okuyama host and port
    """
    if HOST_PATTERN.match(address):
        return True

    return False


def parse_options():
    """
    Parse command line options.
    """
    description = 'Distributed KVS okuyama Python client.'
    parser = argparse.ArgumentParser(description=description, add_help=False)
    parser.add_argument(
        '-h',
        '--host',
        default='127.0.0.1',
        help='okuyama master node address.',
    )
    parser.add_argument(
        '-p',
        '--port',
        default=8888,
        type=int,
        help='okuyama master node port.',
    )
    parser.add_argument('-k', '--key', help='key')
    parser.add_argument('-v', '--value', help='value')
    parser.add_argument('-d', '--delete', help='delete')
    parser.add_argument('-t', '--tags')
    parser.add_argument(
        '-c',
        '--count',
        type=int,
        default=1,
        help='Number of loop count.',
    )
    parser.add_argument(
        '--version',
        action='version',
        version='okuyama client {0}'.format(__version__),
    )

    args = parser.parse_args()

    return args


def main():
    args = parse_options()
    address = '{0}:{1}'.format(args.host, args.port)
    client = Client()
    client.auto_connect([address])
    logging.basicConfig(level=logging.debug, format=Client.debug_log_format)
    logger = logging.getLogger(__name__)

    if args.delete is not None:
        logger.info(client.execute('delete', key=args.delete))
    elif args.value is not None:
        if args.tags is None:
            logger.info(client.set(args.key, args.value))
        else:
            tags = args.tags.split(',')
            logger.info(client.set(args.key, args.value, tags))
    else:
        logger.info(client.get(args.key))


if __name__ == '__main__':
    main()
