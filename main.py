# main.py

from motor import Stepper
from led import Led, ColorGroup
from display import DisplayGUI
from VL53L0X import Gesture

# Circuit Python Implementation for I2C Access
import board
import busio
import adafruit_vl53l0x
import adafruit_ssd1306

from time import sleep
import RPi.GPIO as GPIO

from multiprocessing import Process, Pipe, Queue, current_process

from logs import setup_logger

import os

# Distance sensors
xshut = [4,11,25]

# LED's
led_pins = [14, 15, 18, 23, 24]

# Variable Declaration
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

def error_handler(e,debug=True):
	if debug is not True:
		os.system("sudo reboot now")
	raise e

# Linear transformation of a variable between two scales X and Y
def transform(x1,x2,y1,y2,i):
	return ((y2-y1)/(x2-x1))(i-x1)+y1


def setup():
	logger = setup_logger()
	logger.info("----- setup() Started -----")
	#Initiliaze I2C
	try:
		i2c = board.I2C()
		logger.info(f"I2C intiailized: {i2c}")
		logger.debug(f"I2C devices: {i2c.scan()}")
	except Error as e:
		logger.exception(e,stack_info=True)
		error_handler(e)

	# Display object setup
	try: 
		disp = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c,addr=0x3d)
		logger.info(f"Display intiailized {disp}")
	except:
		logger.exception(e, stack_info=True)
		error_handler(e)

	try:
		wave = Gesture(xshut,i2c)
		logger.info(f"Gesture() instatiated: {wave}")
	except Error as e:
		logger.exception(e, stack_info=True)
		error_handler(e)


	# Data pipes
	motor1_parent,motor1_child = Pipe()
	motor2_parent,motor2_child = Pipe()


	# Motors [a1,a2,b1,b2]
	motor1 = Stepper([12,16,21,20],motor1_child) 
	motor2 = Stepper([10,22,17,27],motor2_child)


	#LED Display Setup
	for i in led_pins:
		LEDS.append(Led(i))
	sensor_LEDS = ColorGroup(LEDS)


	# LED in Wheels Setup

	p1 = Process(target=motor1.run,name="Motor 1")
	p1.start()
	p2 = Process(target=motor2.run, name="Motor 2")
	p2.start()
	

	# Pass display object to GUI Wrapper that contains neat functions to output to display
	GUI = DisplayGUI(disp)


def main():
	logger.info("----- main() Started -----")
	GUI.write("Welcome to the Stand N' Wave \n Wave your hand near the base to begin \n your experience")
	begin = time.time()
	"""start = False
	logger.info("Initial Hand Detection started.")
	while not start: # Loop to detect initial hand wave that will begin experience
		wave.update()
		if 1 in wave.pos:
			start = True
			begin = time.time()
	logger.info("Hand detected. Beginning main loop")"""

	history = [0 for i in range(0,10)] # adjust length depending on loop execution time

	loop_time = 0
	loop_count = 0
	try:
		while True:
			loop_start = time.time()

			wave.update()
			sensor_LEDS.pattern('R', wave.pos) # how to seed for color changing?

			# transform wave.spd from wave speed scale into motor speed scale
			motor_speed = transform(wave.min_speed,wave.max_speed,Stepper.min_speed,Stepper.max_speed,wave.spd)

			if (wave.waves%2) == 1: # odd vs even amount of waves always control the same motor
				motor1_parent.send(float(motor_speed))
			else:
				motor2_parent.send(float(motor_speed))


			# reshape history array into only checking second sensor at index 1
			if 0 not in [wave.history[i][1] for i in range(0,len(wave.history))]:
				motor1_parent.send(float(0)) 
				motor2_parent.send(float(0))
				wave.waves = 0 # reset wave counter so you can spin the cylinders the other way
				

			# Timeout handling for displaying message, stats, and shutting down
			timeout = time.time() - np.max(wave.time)
			if timeout >= 5:
				if timeout <=10:
					motorSpdAve = (motor1.speed_max + motor2.speed_max)/2
					message_seed = floor(transform(wave.min_speed,wave.max_speed,0,5,motorSpdAve)) # Are messages ordered from calm to agitated?
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
					runtime = time.time()-begin
					stats = [f"Total Revolutions: {rev1}/{rev2}", f"Max Speed (rps): {maxSpd1}/{maxSpd2}", f"Runtime (s): {runtime}"]
					GUI.showStats(stats)
				elif timeout <= 30:
					GUI.write("Stand N' Wave will begin shutdown in 10 seconds \n unless user input is detected...")
				elif timeout <= 40:
					GUI.write("Shutting Down...")
					break
			else:
				pass
				# GUI.animation() # We could possibbly have a little animation of a standing wave play
			loop_end = time.time()
			loop_time += loop_end - loop_start
			loop_count += 1
	except KeyboardInterrupt:
		motor1_parent.send("END")
		motor2_parent.send("END")
		p1.terminate()
		p1.join()
		p2.terminate()
		p2.join()
		print(f"Average Loop Completion Time: {loop_time/loop_count}")
		print("User terminated.")
		
	motor1_parent.send("END")
	motor2_parent.send("END")
	p1.terminate()
	p1.join()
	p2.terminate()
	p2.join()
	logger.info(f"Average Loop Completion Time: {loop_time/loop_count}")	
	GUI.write("Stand 'N Wave is \n now safe to unplug.")



if __name__ == '__main__':
	setup()
	main()
	

