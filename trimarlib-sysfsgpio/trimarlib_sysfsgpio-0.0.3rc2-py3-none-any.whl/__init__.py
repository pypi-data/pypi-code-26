# encoding UTF-8

import logging
import os
import os.path
import select
import time
import threading
from .version import VERSION


__all__ = ['get_pins', 'Event', 'Pin']

_logger = logging.getLogger('sysfsgpio')


def get_pins():
    """Returns a list of Pin objects available in the system."""
    pins = []
    entries = os.listdir('/sys/class/gpio')
    _logger.debug('there are %d entries in /sys/class/gpio: %s', len(entries), entries)
    for e in entries:
        if e.startswith('gpiochip'):
            _logger.debug('ignoring chip device: %s', e)
        elif not e.startswith('gpio'):
            _logger.debug('ignoring non-pin entry: %s', e)
        else:
            try:
                pinnum = int(e[4::])
            except ValueError:
                _logger.exception('failed to parse: %s', e, exc_info=False)
                continue
            pins.append(Pin(pinnum))
            _logger.debug('found %s', pins[-1].pinname)
    return pins


class Event(object):
    """Wrapper around a list of callbacks.

    This class overloads operators for convenient manipulation of
    handlers. After initialization the internal handlers list is empty,
    callbacks may be added and removed using incremental
    addition/subtraction operators ('+=' and '-='). Adding already
    registered handler has no effect. Handlers list is internally
    protected with a lock, therefore this class is thread-safe. The
    class overloads __call__ method as well - calling an instance
    invokes all registered callbacks, handling any exceptions raised
    from within.
    """

    def __init__(self):
        self._handlers = []
        self._lock = threading.Lock()

    def __call__(self, *args, **kwargs):
        """Invokes all registered handlers passing positional and
        keyword arguments.
        """
        with self._lock:
            for hdlr in self._handlers:
                try:
                    hdlr(*args, **kwargs)
                except:
                    _logger.exception('caught from handler: %s', hdlr)
        return

    def __iadd__(self, other):
        """Appends callable object to handlers list. Raises TypeError if
        object to be appended is not callable. Has no effect if object
        is already in the list.
        """
        if callable(other):
            with self._lock:
                if other not in self._handlers:
                    self._handlers.append(other)
                else:
                    _logger.debug('%s already in handlers list', other)
        else:
            raise TypeError()
        return self

    def __isub__(self, other):
        """Removes object from the list. Has no effect if object has not
        been registered.
        """
        with self._lock:
            if other in self._handlers:
                self._handlers.remove(other)
            else:
                _logger.debug('%s not found in hadlers list', other)
        return self

    def __len__(self):
        """Returns length of the handlers list (count of registered
        callable objects).
        """
        return len(self._handlers)


class Pin(object):
    """This class is a utility wrapper around sysfs GPIO interface."""

    def __init__(self, pin, direction='in', invert=None):
        """Initializes new object.

        Parameters
        ----------
        pin : number or name of the pin to use
        direction : initial direction of the pin, defaults to 'in'
        invert : initial logic level of the pin
        """
        self._thread = None
        self._thread_lock = threading.Lock()
        self._thread_cancel = threading.Event()
        self._input_changed = Event()
        self._input_changed_lock = threading.Lock()

        self._config = dict(debounce=.1, ontime=-1.0, offtime=-1.0, repeat=-1)

        try:
            self._pin = int(pin)
        except ValueError as e:
            if type(pin) is str:
                if pin[0] != 'P':
                    raise ValueError('pin: expecting int or str name in format PA0, PA1, PB13, etc.')
                port_num = 'ABCDEFGHIJKL'.find(pin[1])
                if port_num < 0:
                    raise ValueError('pin: port out of range')
                pin_num = int(pin[2::], 10)
                if pin_num < 0 or pin_num > 32:
                    raise ValueError('pin: pin out of range')
                self._pin = int(port_num * 32 + pin_num)
            else:
                raise TypeError from e

        self._path = '/sys/class/gpio/gpio{:d}'.format(self._pin)

        if direction is not None:
            if type(direction) is not str:
                raise TypeError('direction: expected str, got {}'.format(type(direction)))
            if direction not in ['in', 'out']:
                raise ValueError('direction: expecting "on" or "off"')
            with open(os.path.join(self._path, 'direction'), 'w') as fd:
                fd.write(direction)
        if invert is not None:
            if type(invert) is not bool:
                raise TypeError('invert: expected bool, got {}'.format(type(invert)))
            with open(os.path.join(self._path, 'active_low'), 'w') as fd:
                fd.write(str(int(invert)))

        try:
            with open(os.path.join(self._path, 'edge'), 'w') as fd:
                fd.write('none')
        except FileNotFoundError:
            _logger.warning('pin %s does not support interrupts', self.pinname)
        return

    @property
    def pin(self):
        """Returns pin number."""
        return self._pin

    @property
    def pinname(self):
        """Returns pin name."""
        nm = 'P'
        nm += 'ABCDEFHIJKL'[int(self._pin / 32)]
        nm += str(self._pin % 32)
        return nm

    @property
    def input_changed(self):
        """Gets or sets "input changed" Event."""
        return self._input_changed

    @input_changed.setter
    def input_changed(self, value):
        if type(value) is not Event:
            raise TypeError('expecting Event, got {}'.format(type(value)))
        with self._input_changed_lock:
            self._input_changed = value

    @property
    def value(self):
        """Gets or sets pin value.

        Raises RuntimeError when attempting to set pin value and worker
        thread is running.
        """
        with open(os.path.join(self._path, 'value'), 'r') as fd:
            return int(fd.read())

    @value.setter
    def value(self, v):
        with self._thread_lock:
            if self._thread is not None and self._thread.is_alive():
                raise RuntimeError('worker thread running')
            with open(os.path.join(self._path, 'value'), 'w') as fd:
                fd.write(str(int(v)))

    @property
    def invert(self):
        """Gets or sets logic level."""
        with open(os.path.join(self._path, 'active_low'), 'r') as fd:
            return bool(int(fd.read()))

    @invert.setter
    def invert(self, v):
        with open(os.path.join(self._path, 'active_low'), 'w') as fd:
            fd.write(str(int(v)))

    @property
    def direction(self):
        """Gets or sets pin direction ('in' or 'out').

        Raises:

        - TypeError when value is not a string;
        - ValueError when value is neither 'in' nor 'out';
        - RuntimeError when attempting to set direction and worker
        thread is running.
        """
        with open(os.path.join(self._path, 'direction'), 'r') as fd:
            return fd.read().strip()

    @direction.setter
    def direction(self, v):
        if type(v) is not str:
            raise TypeError('expecting str, got {}'.format(type(v)))
        elif v not in ['in', 'out']:
            raise ValueError('v = {}'.format(v))
        else:
            with self._thread_lock:
                if self._thread is not None and self._thread.is_alive():
                    raise RuntimeError('worker thread running')
                with open(os.path.join(self._path, 'direction'), 'w') as fd:
                    fd.write(v)

    def config(self, config=None, **kwargs):
        """Gets or sets pin configuration.

        Accepts configuration as keyword arguments or a dictionary.
        Supported fields are:

        - debounce : floating point value representing debouncing delay;
        - ontime : floating point value indicating how long the output
        is held in active state, in seconds;
        - offtime : floating point value indicating how long the output
        is held in inactive state, in seconds;
        - repeat : integer value indicating how many on-off cycles to
        perform, negative value indicates forever.

        Raises:

        - TypeError if unable to cast passed value as target type;
        - RuntimeError if attempting to change configuration and worker
        thread is running.
        """
        if config is None:
            config = kwargs
        if len(config) == 0:
            ret = {}
            for key, value in self._config.items():
                ret[key] = value
            return ret
        with self._thread_lock:
            if self._thread is not None and self._thread.is_alive():
                raise RuntimeError('worker thread running')
            for key in self._config:
                if key in config:
                    try:
                        self._config[key] = type(self._config[key])(config[key])
                    except Exception as e:
                        raise TypeError from e
        return

    @property
    def enabled(self):
        """Enables or disables worker thread of the pin.

        When the pin is configured as input, worker thread monitors pin
        state and invokes callbacks registered using "input_changed"
        property. When the pin is configured as output, worker thread
        performs a on-off cycles according to configuration.
        """
        with self._thread_lock:
            return (self._thread is not None and self._thread.is_alive())

    @enabled.setter
    def enabled(self, value):
        if type(value) is not bool:
            raise TypeError('expecting bool, got {}'.format(type(value)))
        with self._thread_lock:
            tmp = (self._thread is not None and self._thread.is_alive())
            if value == tmp:
                return
            elif value:
                _logger.debug('starting worker thread')
                if self._thread is not None:
                    self._thread.join()
                    self._thread = None
                with open(os.path.join(self._path, 'direction'), 'r') as fd:
                    direction = fd.read().strip()
                if direction == 'in':
                    target = self._input_fun
                    name = 'gpio{}-input'.format(self._pin)
                else:
                    target = self._output_fun
                    name = 'gpio{}-output'.format(self._pin)
                self._thread = threading.Thread(target=target, name=name, daemon=True)
                self._thread.start()
            else:
                _logger.debug('stopping worker thread')
                self._thread_cancel.set()
                self._thread.join()
                self._thread = None
                self._thread_cancel.clear()

    def _input_fun(self):
        cth = threading.current_thread()
        _logger.info('%s started', cth.name)
        try:
            try:
                with open(os.path.join(self._path, 'edge'), 'w') as fd:
                    fd.write('both')
                poll = select.poll()
            except FileNotFoundError:
                poll = None

            with open(os.path.join(self._path, 'value'), 'r') as fd:
                stamp = 0
                v = int(fd.read())
                vv = v
                fd.seek(0)

                if poll is not None:
                    poll.register(fd, select.POLLPRI)
                while not self._thread_cancel.is_set():
                    if poll is not None:
                        ret = poll.poll(self._config['debounce'] * 1000)
                        if len(ret) != 0:
                            vv = int(fd.read())
                            fd.seek(0)
                            continue
                    else:
                        if self._thread_cancel.wait((stamp + self._config['debounce']) - time.time()):
                            continue
                        vv = int(fd.read())
                        fd.seek(0)
                        stamp = time.time()
                    if v != vv:
                        v = vv
                        with self._input_changed_lock:
                            if len(self._input_changed) > 0:
                                self._input_changed(self, v)
                            else:
                                _logger.info('%s, v=%s, no event handler installed', cth.name, v)
        except:
            _logger.exception('%s : input processing failed', cth.name)
        finally:
            try:
                with open(os.path.join(self._path, 'edge'), 'w') as fd:
                    fd.write('none')
            except FileNotFoundError:
                pass
            except:
                _logger.exception('failed to disable interrupts')
        _logger.info('%s exitting', cth.name)
        return

    def _output_fun(self):
        cth = threading.current_thread()
        _logger.info('%s started', cth.name)
        remcnt = self._config['repeat']
        try:
            with open(os.path.join(self._path, 'value'), 'r+') as fd:
                stamp = 0
                while not self._thread_cancel.is_set() and remcnt != 0:
                    v = int(fd.read())
                    fd.seek(0)
                    if v != 0:
                        dly = self._config['ontime']
                        if remcnt > 0:
                            remcnt -= 1
                    else:
                        dly = self._config['offtime']
                    if dly < 0:
                        _logger.debug('steady state, exitting')
                        break
                    self._thread_cancel.wait((stamp + dly) - time.time())
                    fd.write('1' if v == 0 else '0')
                    fd.write('\n')
                    fd.seek(0)
                    stamp = time.time()
                _logger.debug('loop broken')
        except:
            _logger.exception('%s : input processing failed', cth.name)
            return
        _logger.info('%s exitting', cth.name)
        return
