
# coding:utf-8
##### package test #####
import sys
sys.path = ['../../']+sys.path
################
import time
from expy import *  # Import the needed functions

record = []

def close():
    shared.win.close()
    shared.ser.close()
    shared.pyglet.app.exit()

def visualCases(count):
    show(5)

    'flip - trigger send'
    for _ in range(count):
        drawText('Hello', show_now=False)
        drawCircle(30, fill=True, x=0.9, y=-0.9, show_now=False)
        shared.win.flip()
        # sendTrigger(b'\x4d\x21', mode='S')
        cmd_tp = shared.time.time()
        # shared.need_update = False
        record.append([1, getTrigger(), shared.start_tp-cmd_tp])

        show(1) # physical trigger
        show(0.5) # blank screen

    'trigger run + trigger send - flip'
    for _ in range(count):
        drawText('world', show_now=False)
        sendTrigger(b'\x4d\x11', mode='S')
        drawCircle(30, fill=True, x=0.9, y=-0.9) # physical trigger
        cmd_tp = shared.time.time()
        record.append([2, getTrigger(), shared.start_tp-cmd_tp])
        show(1)
        show(0.5) # blank screen

    # 'flip - trigger send'
    # for _ in range(count):
    #     drawText('Hello', show_now=False)
    #     drawCircle(30, fill=True, x=-0.9, y=-0.9,trigger=('mh30', 'S')) # program trigger, physical trigger
    #     cmd_tp = shared.time.time()
    #     record.append([3, getTrigger(), shared.start_tp-cmd_tp])
    #     show(0.5)
    #     show(0.5) # blank screen

def auditoryCases(count):
    show(5)

    sound = makeBeep(440, 1)

    'playing start - trigger send'
    for _ in range(count):
        cmd_tp = shared.time.time()
        playSound(sound,timeit=True)
        record.append([1, getTrigger(), shared.start_tp-cmd_tp])
        print(shared.start_tp-cmd_tp)
        shared.start_tp = None
        show(0.5)

    print()
        

    # 'playing start 2 - trigger send'
    # for _ in range(count):
    #     cmd_tp = shared.time.time()
    #     playSound(sound, timeit=True, triggerbox=True)
    #     print(shared.start_tp-cmd_tp)
    #     shared.start_tp = None
    #     show(0.5)

# start(port='COM5',sample_rate=44100, background_color=C_black)
# auditoryCases(10)
# close()

start(port='COM5', background_color=C_black)
visualCases(5)
close()

start(port='COM5',vsync=True, background_color=C_black)
visualCases(5)
close()

print(record)

