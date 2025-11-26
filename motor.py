# motor.py

import RPi.GPIO as GPIO
from time import sleep
from logs import setup_logger

class Stepper:
	
	FSL = [[1,0,1,0],
		 [0,1,1,0],
		 [0,1,0,1],
		 [1,0,0,1]] # Full Step Logic Table

	# Tested range
	max_speed = 3 # rps
	min_speed = 0.1 # rps

	deceleration = 0.1 # how many rps to decrease each step
	acceleration = 0.1 # how many rps to increase each step



	# Initializing Instance Variables 
	def __init__(self,pins,connection):
		self.pins = pins # [a1, a2, b1, b2] input as list
		self.running = True # Current state of motor
		self.spd = 0 # Current velocity of motor, positive is clockwise, negative is counterclockwise
		self.speed_max = 0 # Maximum speed achieved
		self.step = 0 # Current total step of motor 
		self.conn = connection

		# GPIO Pin Setup
		GPIO.setmode(GPIO.BCM)
		for pin in self.pins:
			GPIO.setup(pin,GPIO.OUT)


	# determines sleep time (s) based on the speed of the motor in rps
	def slp(self):
		try:
			return 1/(200*abs(self.spd))
		except ZeroDivisionError:
			return 0

	def sign(self,speed):
		return 1 if speed > 0 else -1

	# Move function moves the motor one step
	def move(self):
		GPIO.output(self.pins,self.FSL[self.sign(self.spd)*(self.step%len(self.FSL))]) # outputs to each motor pin the logic table entry based on the mod (%) of the total self.step
		#print(self.FSL[self.direction()*(self.step%len(self.FSL))])
		self.step+=1
		sleep(self.slp())


	# Function to call move() N amount of times
	def steps(self,n):
		for i in range(0,n):
			self.move()

	# Indefinetly run move()
	def start(self):
		while True:
			self.move()

	# Multiprocessing implementation of start()
	def run(self):
		logger = setup_logger()
		logger.info(f"{current_process().name} running...")
		targetSpeed = None
		while True:
			
			if self.spd > targetSpeed:
				self.spd -= self.deceleration
			elif self.spd < targetSpeed:
				self.spd += self.acceleration

			if abs(self.spd) >= min_speed: # if it is set below min speed the motor will stop i.e. to 0
				self.move()

			if self.conn.poll():
				msg = self.conn.recv()
				logger.info(f"{current_process().name} Received: {msg}")
				if msg == "END":
				    break
				if msg == "GET":
					self.conn.send([self.step,self.speed_max])
				if type(msg) == float: # More validation on speed input? In main logic perhaps
					if abs(msg) > self.speed_max:
						self.speed_max = abs(msg)
					targetSpeed = msg
					logger.info(f"Current Speed: {self.spd}, Target Speed: {targetSpeed}, Clockwise: {self.clockwise}")
					if self.spd == 0: # if a target speed is received when motor is stopped (self.spd = 0), give it a little speed to start the move() conditional
						self.spd = self.sign(msg)*self.min_speed

		logger.debug(f"{current_process().name} connection closed")
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
