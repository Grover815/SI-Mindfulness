# VL53L0X.py

import board
import busio
import adafruit_vl53l0x
from time import sleep
import math


#Initiliaze I2C
i2c = busio.I2C(board.SCL,board.SDA)


class Gesture():

	max_distance = 200
	min_distance = 0

	def __init__(self,xshut,i2c):
		self.vl53 = []
		self.position = [0 for i in range(0,len(xshut))]
		self.time = [0 for i in range(0,len(xshut))]
		self.speed = 0
		self.direction = 0 # 0 for left, 1 for right
		GPIO.setmode(GPIO.BCM)
		for i in range(0,len(xShut)):
			GPIO.setup(xShut[i], GPIO.OUT, initial=GPIO.LOW)
		for i in range(len(xShut)):
			vl53.append(adafruit_vl53l0x.VL53L0X(i2c))
			vl53[i].start_continuous()       # Hardware/power limitations of using continuous mode?
			vl53[i].set_address(i + 0x30)

	def distance(self):
		distances = [0 for i in range(0,len(vl53))]
		for i, sensor in enumerate(self.vl53):
			distances[i] = (sensor.range)
		return distances

	def is_valid(self,distance):
		return (distance > self.min_distance) and (self.max_distance <200)

	def position(self):
		for i, sensor in enumerate(self.vl53):
			distance = sensor.range
			if is_valid(distance):
				self.position[i] = 1
				self.time = time.time()

	def direction(self):
		self.direction = 1 if (self.position[0]-self.position[-1] < 0) else 0

	def speed(self):
		self.direction()
		self.speed = math.abs(self.position[0]-self.position[-1])


	def update(self):
		ret = True
		try:
			self.position()
			self.direction()
			self.speed()
		except:
			ret = False
		return ret


	def stop():
		for sensor in vl53:
        	sensor.stop_continuous() # Implemenet error handling if other functions are called while continuous ranging is off


if __name__ == 'main':
	pins = [] # Pins for Shutoff pins
	wave = Gesture(pins,i2c)
	try:
		while True:
			wave.update()
			print(wave.position)
	except KeyboardInterrupt:
		wave.stop()
		GPIO.cleanup()
		print("Program Terminated by User.")