# motor.py

import RPi.GPIO as GPIO
from time import sleep


class Stepper:
	
	FSL = [[1,0,1,0],
		 [0,1,1,0],
		 [0,1,0,1],
		 [1,0,0,1]] # Full Step Logic Table

	def __init__(self, pins):
		self.pins = pins # (a1, a2, b1, b2)
		GPIO.setmode(GPIO.BCM)
		for pin in pins:
			GPIO.setup(pin,GPIO.OUT)


	def step(steps,speed,clockwise=True):
		slp = 1/(200*speed*60)
		for i in range(0,steps):
			if clockwise:
				GPIO.output(pins,FSL[i%len(FSL)])
			else:
				GPIO.output(pins,FSL[-i%len(FSL)])
			sleep(slp)

	def stop():
		GPIO.output(pins,(0,0,0,0))
