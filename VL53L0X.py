# VL53L0X.py

import board
import busio
import adafruit_vl53l0x
from time import sleep


#Initiliaze I2C
i2c = busio.I2C(board.SCL,board.SDA)

# Distance Sensor List
vl53 = []

# Shutdown Pins needed
xShut = []

for i in len(xShut):
	GPIO.setup(xShut[i], GPIO.OUT, initial=GPIO.LOW)
for i in len(xShut):
	vl53.append(adafruit_vl53l0x.VL53L0X(i2c))
	vl53[i].start_continuous()       # Hardware/power limitations of using continuous mode?
	vl53[i].set_address(i + 0x30)


GPIO.setup(channel, GPIO.OUT, initial=GPIO.HIGH)


def stop_continuous():
	for sensor in vl53:
        sensor.stop_continuous()

try:
	while True:
		for index, sensor in enumerate(vl53):
			print(f"Distance {index+1}: {sensor.range} mm")
		sleep(1)
except KeyboardInterrupt:
	stop_continuous()
	print("Program Terminated by User.")
	GPIO.cleanup()