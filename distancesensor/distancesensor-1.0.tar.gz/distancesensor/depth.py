import RPi.GPIO as GPIO

import time

GPIO.setmode(GPIO.BOARD)


#set GPIO Pins
front_TRIGGER = 37
front_ECHO = 35

back_TRIGGER = 31
back_ECHO = 33

st_TRIGGER = 38
st_ECHO = 36



#set GPIO direction (IN / OUT)
GPIO.setup(front_TRIGGER, GPIO.OUT)
GPIO.setup(front_ECHO, GPIO.IN)

GPIO.setup(back_TRIGGER, GPIO.OUT)
GPIO.setup(back_ECHO, GPIO.IN)

GPIO.setup(st_TRIGGER, GPIO.OUT)
GPIO.setup(st_ECHO, GPIO.IN)

def depth_front():
    
    GPIO.output(front_TRIGGER, True)

    time.sleep(0.00001)
    GPIO.output(front_TRIGGER, False)
 
    StartTime = time.time()
    StopTime = time.time()
 
    while GPIO.input(front_ECHO) == 0:
        StartTime = time.time()
 
    while GPIO.input(front_ECHO) == 1:
        StopTime = time.time()
    TimeElapsed = StopTime - StartTime
    depth_front = (TimeElapsed * 34300) / 2
    return depth_front


def depth_back():
    
    GPIO.output(back_TRIGGER, True)

    time.sleep(0.00001)
    GPIO.output(back_TRIGGER, False)
 
    StartTime = time.time()
    StopTime = time.time()
 
    while GPIO.input(back_ECHO) == 0:
        StartTime = time.time()
 
    while GPIO.input(back_ECHO) == 1:
        StopTime = time.time()
    TimeElapsed = StopTime - StartTime
    depth_back = (TimeElapsed * 34300) / 2
    return depth_back


def obstacle():
    
    GPIO.output(st_TRIGGER, True)

    time.sleep(0.00001)
    GPIO.output(st_TRIGGER, False)
 
    StartTime = time.time()
    StopTime = time.time()
 
    while GPIO.input(st_ECHO) == 0:
        StartTime = time.time()
 
    while GPIO.input(st_ECHO) == 1:
        StopTime = time.time()
    TimeElapsed = StopTime - StartTime
    obstacle = (TimeElapsed * 34300) / 2
    return obstacle



if __name__ == '__main__':
    try:

        while True:
            dist_f = depth_front()
            print ("Measured front Depth = %.1f cm" % dist_f)
            dist_b = depth_back()
            print ("Measured back Depth = %.1f cm" % dist_b)
	    obst = obstacle()
	    print ("Measured obstacle = %.1f cm" % obst)
	    time.sleep(0.100)
    except KeyboardInterrupt:
        print("Measurement stopped by User")
        GPIO.cleanup()
