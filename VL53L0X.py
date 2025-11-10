# VL53L0X.py

import board
import busio
import adafruit_vl53l0x
from time import sleep


#Initiliaze I2C
i2c = busio.I2C(board.SCL,board.SDA)

# Distance Sensor
vl53 = adafruit_vl53l0x.VL53L0X(i2c)

try:
	while True:
		distance = vl53.range()
		print(f"Distance: {distance}")
		sleep(1)
except KeyboardInterrupt:
	print("Program Terminated by User.")