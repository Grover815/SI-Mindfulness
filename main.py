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

from multiprocessing import Process, Pipe, current_process

from logs import setup_logger
import config

import random

import os
import csv

# Distance sensor pins
xshut = list(map(int,config.cfg('VL53L0X','shutoff').split(',')))

# LED's
led_pins = list(map(int,config.cfg('LED','top_pins').split(',')))
led_pins2 = [int(config.cfg('LED','cylinder_pins'))]

# Motor's [a1,a2,b1,b2]
motor1_pins = list(map(int,config.cfg('Motor','pins1').split(',')))
motor2_pins = list(map(int,config.cfg('Motor','pins2').split(',')))


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
	logger = setup_logger()
	logger.info("Error handler")
	logger.exception(e,stack_info=True)
	raise e
	#os.system("sudo reboot now")
	

# Linear transformation of a variable between two scales X and Y
def transform(x1,x2,y1,y2,i):
	return ((y2-y1)/(x2-x1))*(i-x1)+y1


def main():
	begin = time.time()
	logger = setup_logger()
	logger.info("----- main() Started -----")

	# Set all output pins as low initially
	GPIO.setmode(GPIO.BCM)
	logger.info(f"Distance Sensor Pins: {xshut}")
	logger.info(f"LED Show Pins: {led_pins}")
	logger.info(f"LED cylinder_pins Pins: {led_pins2}")
	logger.info(f"Motor Pins (a1,a2,b1,b2): {motor1_pins}/{motor2_pins}")
	for pin in xshut+led_pins+motor1_pins+motor2_pins+led_pins2:
		try:
			logger.info(f"Pin {pin} setup as LOW OUTPUT")
			GPIO.setup(pin,GPIO.OUT)
			GPIO.output(pin,GPIO.LOW)
		except Exception as e:
			error_handler(e)
	
	#Initiliaze I2C
	try:
		i2c = board.I2C()
		logger.info(f"I2C intiailized: {i2c}")
		logger.info(f"I2C devices: {i2c.scan()}")
	except Exception as e:	
		error_handler(e)


	try:
		wave = Gesture(xshut,i2c)
		logger.info(f"Gesture() instantiated: {wave}")
	except Exception as e:
		logger.exception(e, stack_info=True)
		error_handler(e)


	# Display object setup
	'''
	try: 
		disp = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c,addr=0x3d)
		logger.info(f"Display initialized {disp}")
	except Exception as e:
		logger.exception(e, stack_info=True)
		error_handler(e)
	'''
	# Data pipes
	motor1_parent,motor1_child = Pipe()
	motor2_parent,motor2_child = Pipe()
	#GUI_parent,GUI_child = Pipe()


	# Motors 
	motor1 = Stepper(motor1_pins,motor1_child) 
	motor2 = Stepper(motor2_pins,motor2_child)


	#LED Display Setup
	
	LEDS = []
	for i in led_pins:
		LEDS.append(Led(i))
	sensor_LEDS = ColorGroup(LEDS)
	

	# Pass display object to GUI Wrapper that contains neat functions to output to display
	'''
	try:
		GUI = DisplayGUI(disp)
		logger.info(f"GUI() instatiated: {GUI}")
	except Exception as e:
		logger.exception(e, stack_info=True)
		error_handler(e)
	'''
	# LED in Wheels Setup
	# ....


	# Multiprocessing
	p1 = Process(target=motor1.run,name="Motor 1")
	p1.start()
	p2 = Process(target=motor2.run, name="Motor 2")
	p2.start()
	#p3 = Process(target=GUI.message,name="Display")
	#p3.start()
	

	setup_finished = time.time()

	# Startup LED Sequence
	for ld in LEDS:
		ld.on('B',75)
	#	sleep(0.15)

	#GUI.write("Welcome\nto the\nStand N' Wave")
	#sleep(3)
	#GUI.write("Wave your hand near \n the base to begin \n your experience")

	firstWaveTriggered = False

	endSequenceTriggered = [False,False,False,False,False]
	timeout = int(config.cfg('General','timeout'))

	loop_time = 0
	loop_count = 0
	colors = ['B','G','R']
	try:
		running = True
		logger.info("Main Loop Starting")
		while running:
			loop_start = time.time()

			wave.update()
			if wave.waves == 1 and not firstWaveTriggered:
				firstWaveTriggered = True
				#GUI.write("Experience in Progress")
				GPIO.output(led_pins2,1)

			color_seed = round(transform(wave.min_speed,wave.max_speed,0,2,wave.spd))
			sensor_LEDS.pattern(colors[int(color_seed)], wave.pos) # how to seed for color changing? GBR calmest to fastest

			# transform wave.spd from wave speed scale into motor speed scale
			#print(wave.min_speed,wave.max_speed,Stepper.min_speed,Stepper.max_speed,wave.spd)
			motor_speed = round(transform(wave.min_speed,wave.max_speed,Stepper.min_speed,Stepper.max_speed,wave.spd),1)
			#print(motor_speed)
			if wave.waves%2:
				motor1_parent.send(float(wave.dir*motor_speed))
			else:
				motor2_parent.send(float(wave.dir*motor_speed))




			inputTime = time.time() - wave.timeOn[1]
			holdTime = time.time() - wave.timeOff[1]

			if wave.waves > 0:
				timer = 0
				if inputTime >=timeout:
					timer = inputTime;
				if holdTime >= timeout:
					timer = holdTime
				if timer >= timeout:
					sensor_LEDS.pattern(random.choice(colors), [1,1,1])
					if not endSequenceTriggered[0]:
						logger.info("End Sequence Started")
						motor1_parent.send(float(0))
						motor1_parent.send(float(0))
						GPIO.output(led_pins2,0)
					if timer <= timeout+5 and not endSequenceTriggered[1]:
						logger.info("End Sequence Started")
						endSequenceTriggered[1] = True
						try:
							waveSpdAve = wave.spd_total/wave.spd_count
							message_seed = np.floor(transform(wave.min_speed,wave.max_speed,0,5,waveSpdAve)) # Are messages ordered from calm to agitated?
							#GUI.write(int(message_seed))
							logger.info(f"Message seed: {message_seed} from {wave.spd}")
						except:
							logger.info("No Data to Seed Message")
					if timer <=  timeout+10 and not endSequenceTriggered[2]:
						endSequenceTriggered[2] = True

						# Get Stats
						motor1_stats = [None,None]
						motor2_stats = [None,None]
						motor1_parent.send("GET")
						if motor1_parent.poll():
							motor1_stats = motor1_parent.recv()
							logger.info(f"Motor 1 Stats Received: {motor1_stats}")
						rev1 = motor1_stats[0]
						motorSpdAve1 = motor1_stats[1]

						motor2_parent.send("GET")
						if motor2_parent.poll():
							motor2_stats = motor2_parent.recv()
							logger.info(f"Motor 2 Stats Received: {motor2_stats}")
						rev2 = motor2_stats[0]
						motorSpdAve2 = motor2_stats[1]

						waveCount = wave.waves

						waveSpdAve = None
						try:
							waveSpdAve = wave.spd_total/wave.spd_count
						except ZeroDivisionError:
							waveSpdAve = 4

						stressLevel = None
						try:
							stressLevels = ["Low","Medium","High"]
							stressLevel = stressLevels[round(transform(wave.min_speed,wave.max_speed,0,2,waveSpdAve))]
						except:
							stressLevel = "No Data to Seed Stress Level"

						runtime = loop_time

						stats = [f"Total Revolutions: {rev1}/{rev2}", f"Average Speed (rps): {motorSpdAve1}/{motorSpdAve2}", f"Runtime (s): {runtime}",f"http://10.160.137.193/"]
						logger.info(f"Runtime: {runtime}")
						logger.info(f"Total Revolutions: {rev1}/{rev2}")
						logger.info(f"Average Speed (rps): {motorSpdAve1}/{motorSpdAve2}")
						#GUI.showStats(stats)

						# Sav data into csv
						j = 0 #  counter to not overwrite previous trials
						while os.path.exists(f"logs/stats{j:02}.csv"):
							j+=1
						titles = ['Total Runtime (s)','Stress Level','Average Wave Speed (mm/s)','Wave Count','Total Steps (M1)', 'Average Motor Speed (M1) (rps)','Total Steps (M2)', 'Average Motor Speed (M2) (rps)','Loop Count','Average Loop Completion Time (s)']
						data = [runtime,stressLevel,waveSpdAve,waveCount,rev1,motorSpdAve1,rev2,motorSpdAve2,loop_count,loop_time/loop_count]
						with open(f"logs/stats{j:02}.csv",mode="w",newline="") as file:
							writer = csv.writer(file)
							writer.writerows(zip(titles,data))

					if timer <= timeout+20 and not endSequenceTriggered[3]:
						endSequenceTriggered[3] = True
						#GUI.write("Stand N' Wave will begin shutdown in 10 seconds \n unless user input is detected...")
					if timer <= timeout+30 and not endSequenceTriggered[4]:
						endSequenceTriggered[4] = True
						#GUI.write("Shutting Down...")
						running = False
				else:
					if any(endSequenceTriggered):
						logger.info("End Sequence Interrupted by User input.")
					endSequenceTriggered = [False,False,False,False,False]

			loop_end = time.time()
			loop_time += loop_end - loop_start
			loop_count += 1
	except KeyboardInterrupt:
		print("User terminated.")
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
	logger.info("Main Loop Ended")
	logger.info(f"Loop stats: {loop_count} in average of {loop_time/loop_count} s")
	logger.info(f"Runtime: {runtime}")
	motor1_parent.send("END")
	motor2_parent.send("END")
	p1.join()
	p2.join()
	#wave.stop()
	#GUI.write("Stand 'N Wave is\nnow safe to unplug.")
	GPIO.cleanup()
	logger.info("------- End of Program -------")
	#os.system("sudo shutdow now")

if __name__ == '__main__':
	main()
	

