# main.py

from motor import Stepper
from led import Led, ColorGroup
from display import DisplayGUI
from distance import Gesture

# Circuit Python Implementation for I2C Access
import board
import busio
#import adafruit_vl53l0x
import adafruit_ssd1306

from time import sleep
import time
import RPi.GPIO as GPIO
import numpy as np

from multiprocessing import Process, Pipe, Queue, current_process

from logs import setup_logger

import random

import os
import csv

# Distance sensor pins
xshut = [9,11,0]

# LED's
led_pins = [14, 15, 18, 23, 24]

# Motor's [a1,a2,b1,b2]
motor1_pins = [12,16,21,20]
motor2_pins = [10,22,17,27]


# Variable Declaration
'''
i2c = None
disp = None
wave = None
motor1 = None
motor1_parent,motor1_child = None, None
motor1_parent,motor1_child = None, None
motor2 = None
LEDS = []
sensor_LEDS = []
logger = None
GUI = None
p1 = None
p2 = None
'''

def error_handler(e,debug=True):
	raise e
	if debug is not True:
		os.system("sudo reboot now")
	

# Linear transformation of a variable between two scales X and Y
def transform(x1,x2,y1,y2,i):
	return ((y2-y1)/(x2-x1))*(i-x1)+y1


def main():
	begin = time.time()
	logger = setup_logger()
	logger.info("----- main() Started -----")

	#Initiliaze I2C
	try:
		i2c = board.I2C()
		logger.info(f"I2C intiailized: {i2c}")
		logger.debug(f"I2C devices: {i2c.scan()}")
	except Exception as e:
		logger.exception(e,stack_info=True)
		error_handler(e)


	# Set all output pins as low initially
	GPIO.setmode(GPIO.BCM)
	for pin in xshut+led_pins+motor1_pins+motor2_pins:
		print(pin, "Setup")
		GPIO.setup(pin,GPIO.OUT)
		GPIO.output(pin,GPIO.LOW)




	try:
		wave = Gesture(xshut,i2c)
		logger.info(f"Gesture() instatiated: {wave}")
	except Exception as e:
		logger.exception(e, stack_info=True)
		error_handler(e)

	# Display object setup
	
	try: 
		disp = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c,addr=0x3d)
		logger.info(f"Display intiailized {disp}")
	except Exception as e:
		logger.exception(e, stack_info=True)
		error_handler(e)
	

	# Data pipes
	motor1_parent,motor1_child = Pipe()
	motor2_parent,motor2_child = Pipe()


	# Motors 
	motor1 = Stepper(motor1_pins,motor1_child) 
	motor2 = Stepper(motor2_pins,motor2_child)


	#LED Display Setup
	
	LEDS = []
	for i in led_pins:
		LEDS.append(Led(i))
	sensor_LEDS = ColorGroup(LEDS)
	

	# Pass display object to GUI Wrapper that contains neat functions to output to display
	
	try:
		GUI = DisplayGUI(disp)
		logger.info(f"GUI() instatiated: {GUI}")
	except Exception as e:
		logger.exception(e, stack_info=True)
		error_handler(e)
	
	# LED in Wheels Setup
	# ....


	# Multiprocessing
	p1 = Process(target=motor1.run,name="Motor 1")
	p1.start()
	p2 = Process(target=motor2.run, name="Motor 2")
	p2.start()

	for ld in LEDS:
		ld.on('B',75)
		sleep(0.5)

	setup_finished = time.time()
	GUI.write("Welcome to the Stand \n N' Wave \n Wave your hand near \n the base to begin \n your experience")
	
	"""start = False
	logger.info("Initial Hand Detection started.")
	while not start: # Loop to detect initial hand wave that will begin experience
		wave.update()
		if 1 in wave.pos:
			start = True
			begin = time.time()
	logger.info("Hand detected. Beginning main loop")"""

	#history = [0 for i in range(0,10)] # adjust length depending on loop execution time

	loop_time = 0
	loop_count = 0
	motor_speed1 = 0
	motor_speed2 = 0
	colors = ['G', 'B', 'R']
	loop_start = time.time()
	try:
		while True:
			loop_start = time.time()
			wave.update()
			print(wave.spd)
			randcolor = random.choice(colors)
			color_seed = np.floor(transform(wave.max_speed,wave.min_speed,0,2,wave.spd))
			print(color_seed)
			sensor_LEDS.pattern(colors[int(color_seed)], wave.pos) # how to seed for color changing? GBR calmest to fastest

			# transform wave.spd from wave speed scale into motor speed scale
			'''
			motor_speed = round(transform(wave.min_speed,wave.max_speed,Stepper.min_speed,Stepper.max_speed,wave.spd),1)
			print(f"Motor Speed: {motor_speed}")
			if wave.waves%2:
				motor1_parent.send(float(wave.dir*motor_speed))
			else:
				motor2_parent.send(float(wave.dir*motor_speed))

			
			if (wave.waves%2) == 1: # odd vs even amount of waves always control the same motor
				motor_speed1 = round(transform(wave.min_speed,wave.max_speed,Stepper.min_speed,Stepper.max_speed,wave.spd),1)
				motor1_parent.send(float(motor_speed1))
				motor2_parent.send(float(motor_speed2))
			else:
				motor_speed2 = round(transform(wave.min_speed,wave.max_speed,Stepper.min_speed,Stepper.max_speed,wave.spd),1)
				motor1_parent.send(float(motor_speed1))
				motor2_parent.send(float(motor_speed2))

			'''

			# reshape history array into only checking second sensor at index 1
			if 0 not in [wave.history[i][1] for i in range(0,len(wave.history))]:
				motor1_parent.send(float(0)) 
				motor2_parent.send(float(0))
				wave.waves = 0 # reset wave counter so you can spin the cylinders the other way
				print("Slow down")
				sensor_LEDS.pattern(random.choice(colors), [1,1,1])
		
			timeout = time.time() - np.max(wave.time)
			if timeout >= 20:
				pass

			loop_end = time.time()
			loop_time += loop_end - loop_start
			loop_count += 1




	# Timeout handling for displaying message, stats, and shutting down
	
	
	except KeyboardInterrupt:
		motor1_parent.send("END")
		motor2_parent.send("END")
		p1.terminate()
		p1.join()
		p2.terminate()
		p2.join()
		wave.stop()
		GPIO.cleanup()
		i2c.unlock()
		i2c.deinit()
		logger.info(f"Loop stats: {loop_count} in average of {loop_time/loop_count} s")
		#print(f"Average Loop Completion Time: {loop_time/loop_count}")
		print("User terminated.")
	except Exception as e:
		print("Error caught")
		motor1_parent.send("END")
		motor2_parent.send("END")
		p1.terminate()
		p1.join()
		p2.terminate()
		p2.join()
		GPIO.cleanup()
		i2c.unlock()
		i2c.deinit()
		logger.info(f"Loop stats: {loop_count} in average of {loop_time/loop_count} s")
		logger.exception(e, stack_info=True)
		error_handler(e)
	'''
	timeout = time.time() - np.max(wave.time)
	if timeout >= 5:
		if timeout <=10:
			motorSpdAve = (motor1.speed_max + motor2.speed_max)/2
			message_seed = np.floor(transform(Stepper.min_speed,Stepper.max_speed,0,5,motorSpdAve)) # Are messages ordered from calm to agitated?
			GUI.writeMessage(message_seed)
			logger.info(f"Message seed: {message_seed} from {wave.spd}")
		elif timeout <= 20:
			motor1_stats = [None,None]
			motor2_stats = [None,None]
			motor1_parent.send("GET")
			if motor1_parent.poll():
				motor1_stats = motor1_parent.recv()
				logger.info(f"Motor 1 Stats Received: {motor1_stats}")
			rev1 = motor1_stats[0]
			maxSpd1 = motor1_stats[1]
			motor2_parent.send("GET")
			if motor2_parent.poll():
				motor2_stats = motor2_parent.recv()
				logger.info(f"Motor 2 Stats Received: {motor2_stats}")
			rev2 = motor2_stats[0]
			maxSpd2 = motor2_stats[1]
			runtime = loop_time # time.time() -begin
			stats = [f"Total Revolutions: {rev1}/{rev2}", f"Max Speed (rps): {maxSpd1}/{maxSpd2}", f"Runtime (s): {runtime}"]
			print(stats)
			GUI.showStats(stats)
			# Save stats to CSV file aswell
		elif timeout <= 30:
			print("Shutdown in 10s")
			GUI.write("Stand N' Wave will begin shutdown in 10 seconds \n unless user input is detected...")
		elif timeout <= 40:
			print("Shutting down")
			GUI.write("Shutting Down...")	


	# Save plot as pdf and data into csv
    j = 0 #  counter to not overwrite previous trials
    while os.path.exists(f"logs/stats{j:02}.csv"):
        #print(f"data/accelvtime{j:02} exists.")
        j+=1
    fig.savefig(f"data/accelvtime{j:02}.pdf",format="pdf",bbox_inches='tight')
    times.insert(0,"Times (s)")
    x.insert(0,"X Acceleration (g)")
    y.insert(0,"Y Acceleration (g)")
    z.insert(0,"Z Acceleration (g)")
    with open(f"data/accel_data{j:02}.csv",mode="w",newline="") as file:
        writer = csv.writer(file)
        writer.writerows(zip(times,x,y,z))
    '''
	motor1_parent.send("END")
	motor2_parent.send("END")
	p1.terminate()
	p1.join()
	p2.terminate()
	p2.join()
	wave.stop()
	logger.info(f"Loop stats: {loop_count} in average of {loop_time/loop_count} s")
	print("Unplug now")	
	#GUI.write("Stand 'N Wave is \n now safe to unplug.")



if __name__ == '__main__':
	main()
	

