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

from multiprocessing import Process, Pipe 
#, Event # event use maybe to turn off motors as seen in conditiontest.py

# Distance sensors
xshut = [4,11,25]

# LED's
led_pins = [14, 15, 18, 23, 24]


def main():
	#Initiliaze I2C
	i2c = board.I2C()
	i2c.unlock()

	wave = Gesture(xshut,i2c)

	# Display object setup
	disp = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c,addr=0x3d)


	# Data pipes
	motor1_parent,motor1_child = Pipe()
	motor2_parent,motor2_child = Pipe()


	# Motors
	#motor1 = Stepper([12,16,21,20],motor1_child)
	#motor2 = Stepper([10,22,17,27],motor2_child)


	

	# Pass display object to GUI Wrapper that contains neat functions to output to display
	GUI = DisplayGUI(disp)

	#LED
	LEDS = []
	for i in led_pins:
		print(i)
		LEDS.append(Led(i))
	print(LEDS)
	sensor_LEDS = ColorGroup(LEDS)


	#p1 = Process(target=motor1.run)
	#p1.start()
	#p2 = Process(target=motor2.run)
	#p2.start()
	#GUI.writeMessage(0)
	try:
		for i in range(0,10):
			wave.update()
			sensor_LEDS.pattern('R', wave.pos)
		"""while True:
			if input("Run? (y/n)") == 'n':
				motor1_parent.send("END")
				motor2_parent.send("END")
				break
			motor1_parent.send(float(input("Motor 1 Speed? "))) # speeds between 1 and 4, if 0 motor is stopped but process is still active, negative numbers rotate counter clockwise
			motor2_parent.send(float(input("Motor 2 Speed? ")))	
		p1.terminate()
		p1.join()
		p2.terminate()
		p2.join()
		print("End Message Received.")"""			
	except KeyboardInterrupt:
		p1.terminate()
		p1.join()
		p2.terminate()
		p2.join()
		i2c.unlock()
		print("User terminated.")





if __name__ == '__main__':
	main()
