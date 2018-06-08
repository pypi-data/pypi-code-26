from __future__ import division
import time

# Import the PCA9685 module.
import Adafruit_PCA9685

# Uncomment to enable debug output.
#import logging
#logging.basicConfig(level=logging.DEBUG)

# Initialise the PCA9685 using the default address (0x40).
pwm = Adafruit_PCA9685.PCA9685()

# Alternatively specify a different address and/or bus:
#pwm = Adafruit_PCA9685.PCA9685(address=0x41, busnum=2)

# Configure min and max servo pulse lengths
servo_min = int(1/(1000*(1/50/4096))) #1ms set as Min pulse length.It is then scaled to 4096. Can be changed during use.

servo_max = int(2/(1000*(1/50/4096))) #2ms set as Max pulse length.It is then scaled to 4096. Can be changed during use.

servo_neutral = int(1.5/(1000*(1/50/4096))) #Can be changed during use


# Helper function to make setting a servo pulse width simpler.
def set_servo_pulse(channel, pulse):
    pulse_length = 1000000    # 1,000,000 us per second
    pulse_length /= 50       # 50 Hz
    #print('{0}us per period'.format(pulse_length))
    pulse_length /= 4096     # 12 bits of resolution
    #print('{0}us per bit'.format(pulse_length))
    pulse *= 1000
    pulse /= pulse_length
    if pulse < servo_min and pulse>100:
        pulse = servo_min
    if pulse > servo_max:
        pulse = servo_max
    pulse=int(pulse)
    pwm.set_pwm(channel, 0, pulse)

# Set frequency to 50hz, good for servos.
pwm.set_pwm_freq(50)

def control_servo(channel, angle):
    try:
        if angle <= 180 and angle >=0:
            pulse = 0.5 + angle/180*2
            set_servo_pulse(channel, pulse)
        else:
            print("please enter an angle between 0 to 180 in degrees only!\n")
    except Exception as e:
        print("Error:" + str(e))
