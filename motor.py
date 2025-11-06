# motor.py

import RPi.GPIO as GPIO
from time import sleep
import math
import time

ain1 = 17
ain2 = 27

bin1 = 23
bin2 = 24

pins = (ain1,ain2,bin1,bin2) # tuple of pins to condense gpio toggle

GPIO.setmode(GPIO.BCM)
GPIO.setup(ain1,GPIO.OUT)
GPIO.setup(ain2,GPIO.OUT)
GPIO.setup(bin1,GPIO.OUT)
GPIO.setup(bin2,GPIO.OUT)

# Stepper Motor characteristics
stepsRev = 200


def step(count,clockwise,full,speed):
	steps = []
	slp = 1/(200*speed)
	print(slp)
	if full:
		# two phase on steps
		steps = [[1,0,1,0],
                         [0,1,1,0],
			 [0,1,0,1],
                         [1,0,0,1]]
	else:
		# half steps (double full steps)
		steps = [[1,0,1,0],
			 [0,0,1,0],
			 [0,1,1,0],
			 [0,1,0,0],
			 [0,1,0,1],
			 [0,0,0,1],
			 [1,0,0,1],
			 [1,0,0,0]]
	for i in range(0,count):
                #print(f"Step {i}")
                #print((pins,steps[i%len(steps)]))
                if clockwise: # if not actually clockwise reverse order of cables
                        GPIO.output(pins,steps[i%len(steps)]) # iterate through each step, using mod of steps list index to determine step
                else:
                        GPIO.output(pins,steps[-i%len(steps)])
                sleep(slp) 
                # Time between steps that works (tested)
                # Full step: 0.01 
                # Half Step: 0.0005

def stop():
	GPIO.output(pins,(0,0,0,0))


try:
        starttime = time.time()

        # Parameters
        revolutions = 2 # minimum of two revolutions for task

        clockwise = True # User defined direction
        full = True # User defined method

        speed = 2 # in rps

        steps = 100

        step(steps,clockwise,full,speed) # Call logic sequences
        stop()

        runtime = time.time()-starttime
        freq = revolutions/runtime
        degrees = 360/stepsRev
        print(f"""Runtime: {runtime} | Revolutions: {revolutions} | Period: {runtime/revolutions} s | Frequency: {freq:.03} rps | Turning Degrees per Step: {degrees} | Steps: {steps}""")
except KeyboardInterrupt:
	stop()
	GPIO.cleanup()
	print("Program terminated by user.")
