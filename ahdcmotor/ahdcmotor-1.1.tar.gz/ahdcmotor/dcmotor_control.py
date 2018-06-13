# DC motor direction and speed control

import RPi.GPIO as GPIO
from time import sleep


GPIO.setmode(GPIO.BOARD)

class Motor:


  #start Pwm and Initialize the motor with control pins"
    def __init__(self, forward_Motion, backward_Motion, control):
        self.forward_Motion = forward_Motion
	self.backward_Motion = backward_Motion
	self.control = control

	GPIO.setup(self.forward_Motion, GPIO.OUT)
	GPIO.setup(self.backward_Motion, GPIO.OUT)
	GPIO.setup(self.control, GPIO.OUT)

	self.pwm_forward = GPIO.PWM(self.forward_Motion, 100)
	self.pwm_backward = GPIO.PWM(self.backward_Motion,100)
	self.pwm_forward.start(0)
	self.pwm_backward.start(0)

	GPIO.output(self.control, GPIO.HIGH)

    def forward(self, speed):

	self.pwm_backward.ChangeDutyCycle(0)
	self.pwm_forward.ChangeDutyCycle(speed)
	print ("forward")

    def backward(self, speed):

        self.pwm_forward.ChangeDutyCycle(0)
        self.pwm_backward.ChangeDutyCycle(speed)
	print ("backward")

    def stop(self):
       #Set the duty cycle of both control pins to zero to stop

        self.pwm_forward.ChangeDutyCycle(0)
        self.pwm_backward.ChangeDutyCycle(0)


#Define motor Pins

#motor1 = Motor(11,13,15)   #fwd, bwd, cntrl
#motor2 = Motor(12,16,18)


