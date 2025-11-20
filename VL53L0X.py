# VL53L0X.py

import board
import busio

import adafruit_vl53l0x
from time import sleep
import math
import RPi.GPIO as GPIO
import time




class Gesture():

	
	sensor_distance = 20 # distance between first and last sensor

	def __init__(self,xshut,i2c):
		self.vl53 = []
		self.pos = [0 for i in range(0,len(xshut))]
		self.time = [0 for i in range(0,len(xshut))]
		self.speed = 0
		self.direction = 0 # 0 for left, 1 for right
		self.i2c = i2c
		self.max_distance = 100 # Maximum distance to detect object
		self.min_distance = 0 # Minimum distance to detect object
		
		GPIO.setmode(GPIO.BCM)
		for pin in xshut:
			print(pin, "Setup")
			GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)
		for i in range(0,len(xshut)):
			#GPIO.output(xshut[i],GPIO.HIGH)
			self.vl53.append(adafruit_vl53l0x.VL53L0X(self.i2c,address=0x29))
			self.vl53[i].start_continuous()       # Hardware/power limitations of using continuous mode?
			#self.vl53[i].set_address(i + 0x29)

	def distance(self):
		distances = [0 for i in range(0,len(self.vl53))]
		for i, sensor in enumerate(self.vl53):
			distances[i] = sensor.range
		return distances

	def is_valid(self,distance):
		return (distance > self.min_distance) and (distance < self.max_distance)

	def position(self):
		for i, sensor in enumerate(self.vl53):
			distance = sensor.range
			if self.is_valid(distance):
				self.pos[i] = 1
				self.time[i] = time.time()
			else:
				self.pos[i] = 0

	def direction(self):
		self.direction = 1 if (self.time[0]-self.time[-1] < 0) else 0 

	def speed(self):
		self.direction()
		self.speed = sensor_distance/math.abs(self.time[0]-self.time[-1]) 


	def update(self):
		ret = True
		try:
			self.position()
			self.speed()
		except:
			ret = False
		return ret


	def stop(self):
		for sensor in self.vl53:
			sensor.stop_continuous() # Implemenet error handling if other functions are called while continuous ranging is off


if __name__ == '__main__':
	print("Initializing")
	#Initiliaze I2C
	i2c = board.I2C()
	sensor = adafruit_vl53l0x.VL53L0X(i2c,address=0x29)
	sensor.start_continuous()
	print(sensor.range)
	pins = [5] # Pins for Shutoff pins
	wave = Gesture(pins,i2c)
	try:
		while True:
			wave.position()
			print(wave.pos) # wave.position
			sleep(1)
	except KeyboardInterrupt:
		wave.stop()
		GPIO.cleanup()
		print("Program Terminated by User.")