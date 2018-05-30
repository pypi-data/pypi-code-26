# coding:utf-8
##### package test #####
import sys
sys.path = ['../../']+sys.path
################
import time
from expy import *  # Import the needed functions

# print('vsync=False')
# start()
# show(0.1)
# for _ in range(10):
#     now = time.time()
#     shared.win.flip()
#     print('%.5f' %(time.time() - now))
# shared.win.close()

# print('vsync=True')
# start(vsync=True)
# show(0.1)
# for _ in range(10):
#     now = time.time()
#     shared.win.flip()
#     print('%.5f' %(time.time() - now))
# shared.win.close()

# Zero-setting
def reset():
    sendTrigger(b'\x4d\x00', mode='S')
    show(0.15)

def close():
    sendTrigger(b'\x4d\x00', mode='S') # close signal
    shared.win.close()
    shared.ser.close()
    shared.pyglet.app.exit()

def visualCases(count):

    'flip - trigger send'
    for _ in range(count):
        reset()
        drawText('Hello', show_now=False)
        drawCircle(30, fill=True, x=-0.9, y=-0.9, show_now=False)
        sendTrigger(b'\x4d\x01', mode='S') # program trigger
        show(0.5) # physical trigger
        show(0.5)

    'trigger run + trigger send - flip'
    for _ in range(count):
        reset()
        drawText('Hello', show_now=False)
        drawCircle(30, fill=True, x=-0.9, y=-0.9) # physical trigger
        sendTrigger(b'\x4d\x02', mode='S') # program trigger
        show(0.5)
        show(0.5)

    'flip - trigger send'
    for _ in range(count):
        reset()
        drawText('Hello', show_now=False)
        drawCircle(30, fill=True, x=-0.9, y=-0.9,trigger=(b'\x4d\x03', 'S')) # program trigger, physical trigger
        show(0.5)
        show(0.5)

def auditoryCases(count):
    sound = makeBeep(440, 1)

    'playing start - trigger send'
    for _ in range(count):
        reset()
        sendTrigger(b'\x4d\x04', mode='S') # program trigger
        playSound(sound)
        show(0.5)

    'playing start 2 - trigger send'
    for _ in range(count):
        reset()
        playSound(sound,trigger=(b'\x4d\x05', 'S'))
        show(0.5)

start(port='COM5',sample_rate=44100)
reset()
auditoryCases(5)
close()

start(port='COM5')
reset()
visualCases(5)
close()

start(port='COM5',vsync=True)
reset()
visualCases(5)
close()

