# motor.py

import RPi.GPIO as GPIO
from time import sleep

class Stepper:
	
	FSL = [[1,0,1,0],
		 [0,1,1,0],
		 [0,1,0,1],
		 [1,0,0,1]] # Full Step Logic Table


	# Initializing Instance Variables 
	def __init__(self, pins):
		self.pins = pins # [a1, a2, b1, b2] input as list
		self.running = False # Current state of motor
		self.active = True # State of motor being able to move (i.e. in the start loop)
		self.clockwise = True # Current direction of motor
		self.speed = 0 # Current speed of motor
		self.step = 0 # Current total step of motor 
		self.error = False # Error handling

		# GPIO Pin Setup
		GPIO.setmode(GPIO.BCM)
		print(self.pins)
		for pin in self.pins:
			GPIO.setup(pin,GPIO.OUT)


	# determines sleep time (s) based on the speed of the motor in rpm
	def slp(self):
		return 1/(200*self.speed)

	# determines direction by travering FSL backwards (-1) or forwards (1)
	def direction(self):
		return -1 if not self.clockwise else 1

	# Move function moves the motor one step
	def move(self):
                GPIO.output(self.pins,self.FSL[self.direction()*(self.step%len(self.FSL))]) # outputs to each motor pin the logic table entry based on the mod (%) of the total self.step
                print(self.FSL[self.direction()*(self.step%len(self.FSL))])
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
		while self.active:
			if self.running:
				self.move()
		return "Motor Encountered Error"


# this if statement is only run if the python file is run directly from terminal using python motor.py
# this will not trigger when imported into another file
# this isolation provides a good way to test the motor
if __name__ == '__main__':
        print("~Motor Test~")
        pins = (12,16,21,20)
        #pins = ["A1","A2",'B1',"B2"]
        #for i in range(0,4):
        #        pins[i] = int(input(f"Pin {pins[i]}: "))
        motor = Stepper(pins)
        try:
                newSpeed = True
                while True:
                        if newSpeed:
                                motor.speed = int(input("Speed (rpm): "))
                                newSpeed = False
                                print(motor.slp())
                        motor.steps(200)
                        print("One Rotation Complete")
                        if input("Change Speed (y/n): ") == 'y':
                                newSpeed= True
                        else:
                                newSpeed = False
                print("Done.")
        except KeyboardInterrupt:
                print(f"Total Steps: {motor.step}")
                print("Motor Test Terminated by User.")
                motor.stop()
                GPIO.cleanup()
