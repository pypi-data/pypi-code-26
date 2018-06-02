# pylint:disable=W,C,R
from __future__ import print_function

from collections import deque

from pydbus import SessionBus

import xcffib
import xcffib.xproto
from xpybutil.ewmh import get_active_window

EVENT_QUEUE = deque()

BUS = SessionBus()
ROFI_BUS = BUS.get('pro.wizardsoftheweb.pyrofibus')
CONNECTION = xcffib.connect()
ROOT = CONNECTION.get_setup().roots[0].root
CONNECTION.core.ChangeWindowAttributesChecked(
    ROOT,
    xcffib.xproto.CW.EventMask,
    [xcffib.xproto.EventMask.PropertyChange],
).check()


def fill_queue():
    current_event = CONNECTION.wait_for_event()
    EVENT_QUEUE.appendleft(current_event)
    while True:
        try:
            trailing_event = CONNECTION.poll_for_event()
            if trailing_event:
                EVENT_QUEUE.appendleft(trailing_event)
            else:
                break
        except KeyboardInterrupt:
            exit(0)


def events():
    while len(EVENT_QUEUE):
        yield EVENT_QUEUE.pop()


def consume_event(event):
    atom_name = CONNECTION.core.\
        GetAtomName(event.atom)\
        .reply()\
        .name\
        .to_string()
    if '_NET_ACTIVE_WINDOW' == atom_name:
        ROFI_BUS.UpdateActiveWindow(get_active_window().reply())


def consume_queue():
    for event in events():
        consume_event(event)


def cli():
    while True:
        try:
            fill_queue()
            consume_queue()
        except KeyboardInterrupt:
            exit(0)

if '__main__' == __name__:
    cli()
