# motor.py

import RPi.GPIO as GPIO
from time import sleep

class Stepper:
	
	FSL = [[1,0,1,0],
		 [0,1,1,0],
		 [0,1,0,1],
		 [1,0,0,1]] # Full Step Logic Table


	# Initializing Instance Variables 
	def __init__(self,pins,connection):
		self.pins = pins # [a1, a2, b1, b2] input as list
		self.running = True # Current state of motor
		self.clockwise = True # Current direction of motor
		self.speed = 0 # Current speed of motor
		self.step = 0 # Current total step of motor 
		self.error = False # Error handling
		self.coast = True
		self.conn = connection

		# GPIO Pin Setup
		GPIO.setmode(GPIO.BCM)
		print(self.pins)
		for pin in self.pins:
			GPIO.setup(pin,GPIO.OUT)


	# determines sleep time (s) based on the speed of the motor in rps
	def slp(self):
		return 1/(200*self.speed)

	# determines direction by travering FSL backwards (-1) or forwards (1)
	def direction(self):
		return -1 if not self.clockwise else 1

	# Move function moves the motor one step
	def move(self):
		GPIO.output(self.pins,self.FSL[self.direction()*(self.step%len(self.FSL))]) # outputs to each motor pin the logic table entry based on the mod (%) of the total self.step
		#print(self.FSL[self.direction()*(self.step%len(self.FSL))])
		self.step+=1
		sleep(self.slp())

	# stop function
	def stop(self):
		self.run = False

	# Function to call move() N amount of times
	def steps(self,n):
		for i in range(0,n):
			self.move()

	# Indefinetly run move()
	def start(self):
		while self.running: # not self.runninng.is_set()
			self.move()
			if self.coast:
				self.speed -= 0.1 # Deacceleration strategry?
			if self.speed <= 0.5:
				break
		print("Motor stopped.")

	# Multiprocessing implementation of start()
	def run(self):
		while True:
			if self.conn.poll():
				msg = self.conn.recv()
				if msg == "END":
				    break
				if type(msg) == int: # More validation on speed input? In main logic perhaps
					#print(msg)
					self.speed = abs(msg)
					self.clockwise = True if msg > 0 else False
			if self.speed>= 0.5:
				self.move()
		self.conn.close()


# this if statement is only run if the python file is run directly from terminal using python motor.py
# this will not trigger when imported into another file
# this isolation provides a good way to test the motor
"""
if __name__ == '__main__':
	#from multiprocessing import
	print("~Motor Test~")
	pins = (12,16,21,20)
	#pins = ["A1","A2",'B1',"B2"]
	#for i in range(0,4):
	#        pins[i] = int(input(f"Pin {pins[i]}: "))
		motor = Stepper(pins, True)
	try:
		motor.speed = int(input("Speed (rpm): "))
		print(motor.slp())
		motor.start() # Test if deacceleration of motors work with coasting variable !!
	except KeyboardInterrupt:
		print(f"Total Steps: {motor.step}")
		print("Motor Test Terminated by User.")
		motor.stop()
		GPIO.cleanup()
"""
