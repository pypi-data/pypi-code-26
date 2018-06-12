
from . import Pin, __version__
import argparse
import threading
import logging
import signal

__logger__ = logging.getLogger(__name__)

def test(input_pin, output_pin, repeat_count):
    cancel = threading.Event()
    fmt = '%(asctime)s %(levelname)s %(name)s:%(funcName)s %(message)s'
    logging.basicConfig(level=logging.DEBUG, format=fmt)

    def sig_handler(signum, frame):
        __logger__.debug('signal caught: %s\nframe: %s', signal.getsignal(signum), frame)
        cancel.set()

    def input_handler1(sender, value):
        __logger__.debug('invoked by %s (%s), v=%s', sender, sender.pinname(), value)
        raise RuntimeError()

    def input_handler2(sender, value):
        __logger__.debug('invoked by %s (%s), v=%s', sender, sender.pinname(), value)
        return

    signal.signal(signal.SIGTERM, sig_handler)
    pout = Pin(output_pin, direction='out')
    pin = Pin(input_pin, direction='in', invert=True)
    
    __logger__.info('starting test, input pin is %s, output pin is %s, repeat count is %d',
                    pin.pinname(), pout.pinname(), repeat_count)

    pout.config(ontime=.5, offtime=.25, repeat=repeat_count)
    pin.enabled(True)
    pout.enabled(True)
    try:
        while pout.enabled():
            if cancel.wait(.5):
                break
    except:
        __logger__.exception('terminating')
    if not cancel.is_set():
        pin.input_changed += input_handler1
        pin.input_changed += input_handler1
        pin.input_changed += input_handler2
        pout.enabled(True)
        try:
            while pout.enabled():
                if cancel.wait(.5):
                    break
        except:
            __logger__.exception('terminating')
    pin.input_changed -= input_handler1
    pin.input_changed -= input_handler2
    pin.input_changed -= input_handler2
    pin.enabled(False)
    __logger__.info('exit')
    return


parser = argparse.ArgumentParser()
parser.add_argument('op', type=str, choices=['test'])
parser.add_argument('--output', default='PA10')
parser.add_argument('--input', default='PA20')
parser.add_argument('--repeat', type=int, default=2)
parser.add_argument('--version', action='version', version='sysfsgpio v{}'.format(__version__))
ns = parser.parse_args()

if ns.op == 'test':
    test(ns.input, ns.output, ns.repeat)
    exit(0)
print('Unknown operation.')
exit(-1)
