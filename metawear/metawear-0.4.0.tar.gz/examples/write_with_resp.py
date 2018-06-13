from mbientlab.warble import *

from collections import deque
from ctypes import *
from time import sleep
from threading import Event

import sys

e = Event()

print(sys.argv[1])
gatt = Gatt(sys.argv[1])
gatt.connect_async(lambda error: e.set())
e.wait()

print("connected")
e.clear()

samples = 0
def value_changed(value):
    print(str(value))
    global samples
    samples += 1
notify = gatt.find_characteristic("326a9006-85cb-9195-d9dd-464cfbbae75a")
notify.on_notification_received(value_changed)
notify.enable_notifications_async(lambda error: e.set())
e.wait()

cmd = gatt.find_characteristic("326a9001-85cb-9195-d9dd-464cfbbae75a")
values = deque([
    [0x1, 0x80],
    [0x2, 0x80],
    [0x3, 0x80],
    [0x4, 0x80],
    [0x5, 0x80],
    [0x6, 0x80],
    [0x7, 0x80],
    [0x8, 0x80],
    [0x9, 0x80],
    [0xa, 0x80],
    [0xb, 0x80],
    [0xc, 0x80],
    [0xd, 0x80],
    [0xf, 0x80],
    [0x10, 0x80],
    [0x11, 0x80],
    [0x12, 0x80],
    [0x13, 0x80],
    [0x14, 0x80],
    [0x15, 0x80],
    [0x16, 0x80],
    [0x17, 0x80],
    [0x18, 0x80],
    [0xfe, 0x80]
])
def write_values():
    if len(values) == 0:
        e.set()
    else:
        def completed(error):
            if error != None:
                print(error)
            write_values()
        cmd.write_async(values.popleft(), completed)

chars = deque([
    "00002a26-0000-1000-8000-00805f9b34fb",
    "00002a24-0000-1000-8000-00805f9b34fb",
    "00002a27-0000-1000-8000-00805f9b34fb",
    "00002a29-0000-1000-8000-00805f9b34fb",
    "00002a25-0000-1000-8000-00805f9b34fb"
])
def read_gatt_chars():
    if len(chars) == 0:
        write_values()
    else:
        gattchar = gatt.find_characteristic(chars.popleft())
        if gattchar != None:
            def completed(value, error):
                if error == None:
                    print("%s: %s" % (gattchar.uuid, bytearray(value).decode('ascii')))
                    read_gatt_chars()
                else:
                    print("%s: Error reading gatt char (%s)" % (gattchar.uuid, error))

            gattchar.read_value_async(completed)
        else:
            print("%s: does not exist" % gattchar.uuid)
            read_gatt_chars()

e.clear()
read_gatt_chars()
e.wait()

e.clear()
#cmd.write_without_resp_async([0x11, 0x09, 0x06, 0x00, 0x06, 0x00, 0x00, 0x00, 0x58, 0x02], lambda error: e.set())
#e.wait()

#sleep(2.0)
#e.clear()

#values = deque([
#    [0x03, 0x03, 0x29, 0x0c], 
#    [0x03, 0x02, 0x01, 0x00],
#    [0x03, 0x04, 0x01],
#    [0x13, 0x03, 0x29, 0x00],
#    [0x13, 0x05, 0x01],
#    [0x13, 0x02, 0x01, 0x00],
#    [0x03, 0x01, 0x01],
#    [0x13, 0x01, 0x01]
#])

sleep(30.0)

print("samples: " + str(samples))

gatt.on_disconnect(lambda status: e.set())
cmd.write_async([0xfe, 0x01], lambda status: None)

e.wait()
print("disconnected")
