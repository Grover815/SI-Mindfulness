# main.py

from motor import Stepper
from led import Led
from display import DisplayGUI

# Circuit Python Implementation for I2C Access
import board
import busio
import adafruit_vl53l0x
import adafruit_ssd1306

from multiprocessing import Process

#Initiliaze I2C
i2c = busio.I2C(board.SCL,board.SDA)

# Distance Sensors
vl53 = adafruit_vl53l0x.VL53L0X(i2c)
sensors = []


# Display object setup
disp = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)

# Motors
motor1 = Stepper([0,0,0,0])
motor2 = Stepper([0,0,0,0])

# Pass display object to GUI Wrapper that contains neat functions to output to display
#GUI = DisplayGUI(disp)


def main():
	p1 = Process(target=motor1.start)
	p1.start()
	p2 = Process(target=motor2.start)
	p2.start()

	while True:
		if input("Run? (y/n)") == 'y':
			motor1.running = True
			motor2.running = True
		else:
			motor1.running = False
			motor2.running = False
			break
	


	p1.join()
	p2.join()



if __name__ == '__main__':
	main()