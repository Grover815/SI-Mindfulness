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
		self.run = False
		self.clockwise = True
		self.speed = 0
		self.step = 0
		self.error = False

		GPIO.setmode(GPIO.BCM)
		for pin in pins:
			GPIO.setup(pin,GPIO.OUT)


	def step(self,steps,speed,clockwise=True):
		slp = 1/(200*speed*60)
		n = 1
		if clockwise:
			n=1
		else:
			n=-1
		for i in range(0,steps):
			GPIO.output(self.pins,FSL[n*(i%len(FSL))])
			sleep(slp)

	def start(self):
		while not self.error:
			if self.run:
				self.move()
		return "Motor Encountered Error"

	def slp(self):
		return 1/(200*self.speed*60)

	def direction(self):
		return -1 if not self.clockwise else 1

	def move(self):
		GPIO.output(self.pins,FSL[self.direction()*(self.step%len(FSL))])
		self.step+=1
		sleep(self.slp())

	def stop(self):
		self.run = False
		self.error = True


if __name__ == '__main__':
	print("~Motor Test~")
	pins = ["A1","A2",'B1',"B2"]
	for i in range(0,3):
		pins[i] = input(f"Pin {pins[i]}: ")
	motor = Stepper(pins)
	try:
		while True:
			speed = input("Speed (rpm): ")
			motor.step(200,speed)
			print("One Rotation Complete")
	except KeyboardInterrupt:
		print("Motor Test Terminated by User.")
		motor.stop()
		GPIO.cleanup()
