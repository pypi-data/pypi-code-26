#!/usr/bin/env python
# pylint:disable=W,C,R
import sys
from pydbus import SessionBus
from xpybutil.ewmh import get_desktop_names, get_wm_desktop, get_wm_name
from xpybutil.util import get_property


def cli():
    ARGS = sys.argv[1:]
    bus = SessionBus()
    rofi_bus = bus.get('pro.wizardsoftheweb.pyrofibus')

    if ARGS and ARGS[0]:
        rofi_bus.ActivateWindow(int(ARGS[0].split(' ')[-1]))
        exit(0)

    window_ids = rofi_bus.GetWindowList()
    desktops = get_desktop_names().reply()
    items = []
    max_desktop = 0
    max_class = 0
    max_name = 0
    for window_id in window_ids:
        new_item = [
            desktops[get_wm_desktop(window_id).reply()],
            get_property(window_id, 'WM_CLASS')
            .reply()
            .value
            .to_string()
            .split('\x00')[1],
            get_wm_name(window_id).reply().encode('utf-8'),
            window_id,
        ]
        max_desktop = len(new_item[0]) if len(
            new_item[0]) > max_desktop else max_desktop
        max_class = len(new_item[1]) if len(
            new_item[1]) > max_class else max_class
        max_name = len(new_item[2]) if len(
            new_item[2]) > max_name else max_name
        items.append(new_item)
    items.append(items.pop(0))

    for item in items:
        print(
            "{:{max_desktop}} {:{max_class}} {:{max_name}} {}".format(
                *item,
                max_desktop=max_desktop + 2,
                max_class=max_class + 2,
                max_name=max_name
            )
        )

if '__main__' == __name__:
    cli()
