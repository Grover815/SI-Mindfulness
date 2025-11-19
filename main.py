# main.py

from motor import Stepper
#from led import Led
from display import DisplayGUI

# Circuit Python Implementation for I2C Access
import board
import busio
#import adafruit_vl53l0x
import adafruit_ssd1306

from multiprocessing import Process, Pipe 
#, Event # event use maybe to turn off motors as seen in conditiontest.py

# Distance sensors
xshut = []

# LED's
leds = []


def main():
	#Initiliaze I2C
	i2c = busio.I2C(board.SCL,board.SDA)

	# Display object setup
	disp = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c,addr=0x3d)


	# Data pipes
	motor1_parent,motor1_child = Pipe()
	motor2_parent,motor2_child = Pipe()


	# Motors
	motor1 = Stepper([12,16,21,20],motor1_child)
	motor2 = Stepper([10,22,17,27],motor2_child)


	#wave = Gesture(xshut,i2c)

	# Pass display object to GUI Wrapper that contains neat functions to output to display
	GUI = DisplayGUI(disp)

	#LED
	#for i in range(0,len(led)):
	#	leds[i] = Led(led)


	p1 = Process(target=motor1.run)
	p1.start()
	p2 = Process(target=motor2.run)
	p2.start()
	GUI.writeMessage("Resistance makes \n success worthwhile.")
	try:
		while True:
			if input("Run? (y/n)") == 'n':
				motor1_parent.send("END")
				motor2_parent.send("END")
				break
			motor1_parent.send(int(input("Motor 1 Speed? "))) # speeds between 1 and 4, if 0 motor is stopped but process is still active, negative numbers rotate counter clockwise
			motor2_parent.send(int(input("Motor 2 Speed? ")))	
		p1.terminate()
		p1.join()
		p2.terminate()
		p2.join()
		print("End Message Received.")			
	except KeyboardInterrupt:
		p1.terminate()
		p1.join()
		p2.terminate()
		p2.join()
		GUI.writeMessage("")
		print("User terminated.")





if __name__ == '__main__':
	main()
