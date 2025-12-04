# motor.py

import RPi.GPIO as GPIO
from time import sleep
from logs import setup_logger
from multiprocessing import current_process
import time
import config


class Stepper:
	
	FSL = [[1,0,1,0],
		 [0,1,1,0],
		 [0,1,0,1],
		 [1,0,0,1]] # Full Step Logic Table

	# Tested range
	max_speed = float(config.cfg('Motor','max_speed')) # rps
	min_speed = float(config.cfg('Motor','min_speed')) # rps

	deceleration = 0.1 # how many rps to decrease each step
	acceleration = 0.1 # how many rps to increase each step


	# Initializing Instance Variables 
	def __init__(self,pins,connection):
		self.pins = pins # [a1, a2, b1, b2] input as list
		self.running = True # Current state of motor
		self.spd = 0 # Current velocity of motor, positive is clockwise, negative is counterclockwise
		self.speed_total = 0 # Maximum speed achieved
		self.speed_count = 0
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
		targetSpeed = 0
		targetSpeed_time = time.time()
		while True:
			if self.spd > targetSpeed:
				self.spd -= self.deceleration
			elif self.spd < targetSpeed:
				self.spd += self.acceleration

			'''
			if self.spd == targetSpeed:
				targetSpeed_time = time.time()
				if time.time() - targetSpeed_time >= 10:
					targetSpeed = 0
			'''
			if abs(self.spd) >= self.min_speed: # if it is set below min speed the motor will stop i.e. to 0
				self.move()
				self.spd = round(self.spd,1)

			if self.conn.poll():
				msg = self.conn.recv()
				if msg == "END":
				    break
				if msg == "GET":
					self.conn.send([self.step,self.speed_total/self.speed_count])
				if type(msg) == float: # More validation on speed input? In main logic perhaps
					if msg != targetSpeed:  # if a new target speed has been sent
						logger.info(f"{current_process().name} Received New Speed: {msg}")
						targetSpeed = msg
						logger.info(f"Current Speed: {self.spd}, Target Speed: {targetSpeed}")
						self.speed_total+=targetSpeed
						self.speed_count+=1
						if self.spd == 0: # if a target speed is received when motor is stopped (self.spd = 0), give it a little speed to start the move() conditional
							self.spd = self.sign(msg)*self.min_speed + 0.1

		logger.debug(f"{current_process().name} connection closed")
		self.conn.close()


# this if statement is only run if the python file is run directly from terminal using python motor.py
# this will not trigger when imported into another file
# this isolation provides a good way to test the motor

if __name__ == '__main__':
	from multiprocessing import Process, Pipe, current_process
	print("~Motor Test~")
	#pins = [10,22,17,27]
	pins = [12,16,21,20]
	#pins = ["A1","A2",'B1',"B2"]
	GPIO.setmode(GPIO.BCM)
	for pin in pins:
		GPIO.setup(pin,GPIO.OUT)
		GPIO.output(pin,GPIO.LOW)
	motor_parent,motor_child = Pipe()
	motor = Stepper(pins, motor_child)
	p1 = Process(target=motor.run,name="Motor Test")
	p1.start()
	try:
		while True:
			motor_parent.send(float(input("Motor Speed? ")))
		motor.speed = int(input("Speed (rpm): "))
	except KeyboardInterrupt:
		print("Motor Test Terminated by User.")
		motor_parent.send("END")
		p1.join()
		GPIO.cleanup()

