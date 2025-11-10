# main.py

from motor import Stepper
from led import Led

# Circuit Python Implementation for I2C Access
import board
import busio
import adafruit_vl53l0x
import adafruit_ssd1306

from threading import Thread

#Initiliaze I2C
i2c = busio.I2C(board.SCL,board.SDA)

# Distance Sensors
vl53 = adafruit_vl53l0x.VL53L0X(i2c)
sensors = []


# Display
disp = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)

# Motors
motor1 = Stepper([0,0,0,0])
motor2 = Stepper([0,0,0,0])


def main():
	t1 = Thread(target=motor1.start)
	t2 = Thread(target=motor2.start)
	while True:
		pass


	t1.join()
	t2.join()



if __name__ == '__main__':
	main()