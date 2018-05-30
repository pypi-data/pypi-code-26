'''
The MIT License (MIT)

Copyright (c) 2018 Hudson Nobles

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation 
files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, 
modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software 
is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF 
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE 
FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION 
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
import socket
global ip, port
ip = '192.168.10.1'
port = 8889

def start():
    transmit("command")

def setAddr(input_ip=None, input_port=None):
    global ip,port
    if input_ip == None:
            ip = "192.168.10.1"
    else:
        ip = input_ip
    if input_port == None:
        port = 8889
    else:
        port = input_port

def transmit(command):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    command = command.encode('utf-8')
    sock.sendto(command, (ip,port))

def getResponse():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ret = sock.recv(1024)
    return ret

def takeoff():
    transmit("takeoff")

def land():
    transmit("land")

def up(dist):
    if (dist < 20 or dist > 500):
        dist = 20
    command = "up " + str(dist)
    transmit(command)

def down(dist):
    if (dist < 20 or dist > 500):
        dist = 20
    command = "down " + str(dist)
    transmit(command)
    
def left(dist):
    if (dist < 20 or dist > 500):
        dist = 20
    command = "left " + str(dist)
    transmit(command)

def right(dist):
    if (dist < 20 or dist > 500):
        dist = 20
    command = "right " + str(dist)
    transmit(command)

def forward(dist):
    if (dist < 20 or dist > 500):
        dist = 20
    command = "forward " + str(dist)
    transmit(command)
    
def back(dist):
    if (dist < 20 or dist > 500):
        dist = 20
    command = "back " + str(dist)
    transmit(command)

def rot_clockwise(deg):
    command = "cw " + str(deg)
    transmit(command)

def rot_counterclockwise(deg):
    command = "ccw " + str(deg)
    transmit(command)
    
def flip(Dir):
    command = "flip " + Dir
    transmit(command)

def setSpeed(spd):
    if (spd < 1 or spd > 100):
        spd = 0
    command = 'speed '+ str(spd)
    transmit(command)

def getSpeed():
    transmit("Speed?")
    response = getResponse()
    return response

def getBattery():
    transmit("Battery?")
    response = getResponse()
    return response

def getTime():
    transmit("Time?")
    response = getResponse()
    return response    
