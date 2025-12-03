# VL53L0X.py

import adafruit_vl53l0x
from time import sleep
import RPi.GPIO as GPIO
import time
import config




class Gesture():

	
	max_distance = int(config.cfg('VL53L0X','detection_max')) # Maximum distance to detect object
	min_distance = int(config.cfg('VL53L0X','detection_min')) # Minimum distance to detect object
	sensor_distance = int(config.cfg('VL53L0X','sensor_distance')) # distance between first and last sensor
	max_speed = int(config.cfg('VL53L0X','max_speed')) #11 # units? do testing for maximum hand wave speed
	min_speed = int(config.cfg('VL53L0X','min_speed'))


	def __init__(self,xshut,i2c):
		self.i2c = i2c
		self.vl53 = []
		self.pos = [0 for i in range(0,len(xshut))]
		self.history = [[0 for i in range(0,len(xshut))] for i in range(0,300)] # keep the last 10 cycles of data
		self.timeOn = [0 for i in range(0,len(xshut))]
		self.timeOff = [0 for i in range(0,len(xshut))]
		self.triggered = [False for i in range(0,len(xshut))]
		self.spd = 0
		self.dir = 0 # -1 for left, 1 for right
		self.waves = 0
		self.spd_total = 0
		self.spd_count = 0


		
		addrs = [hex(addr) for addr in i2c.scan()]
		
		for i in range(0,len(xshut)):
			GPIO.output(xshut[i],GPIO.HIGH)
			print([hex(addr) for addr in self.i2c.scan()])
			try:
				self.vl53.append(adafruit_vl53l0x.VL53L0X(self.i2c,address=0x29))
			except Exception as e:
				GPIO.output(xshut,[0]*len(xshut))
				i2c.unlock()
				raise e
			self.vl53[i].start_continuous()       # Hardware/power limitations of using continuous mode?
			self.vl53[i].set_address(i + 0x30)

	def distance(self):
		distances = [0 for i in range(0,len(self.vl53))]
		for i, sensor in enumerate(self.vl53):
			#print(f"Distance Read on {i}")
			distances[i] = sensor.range
		return distances

	def is_valid(self,distance):
		return (distance > self.min_distance) and (distance < self.max_distance)

	def position(self):
		self.posPrev = self.pos
		for i, sensor in enumerate(self.vl53):
			#print("time +", self.timeOn)
			distance = sensor.range
			if self.is_valid(distance):
				self.pos[i] = 1
				self.timeOn[i] = time.time()
			else:
				self.pos[i] = 0
				self.timeO[i] = time.time()

	def direction(self):
		self.dir = 1 if (self.timeOn[0]-self.timeOn[-1] < 0) else -1

	def speed(self):
		try:

			self.spd = self.sensor_distance/abs(self.timeOn[0]-self.timeOn[-1]) 
			#print(self.spd)
			# if speed detected greater than maximum speed, set to maximum speed, this will let the motor speed be properly bounded as well
			if self.spd > self.max_speed: 
				self.spd = self.max_speed
			self.spd_total+=self.spd
			self.spd_count+=1
		except ZeroDivisionError:
			self.spd = 0


	def update(self):
		if 0 not in self.timeOn:
			self.position()
			self.history.pop(0)
			self.history.append(self.pos)
		else:
			self.timeOn = [1,1,1]
		
		for i,ele in enumerate(self.pos): 
			if ele == 1:
				#print(i, 'triggered')
				self.triggered[i] = True
				#print(self.triggered)
		
		if False not in self.triggered: # only update speed and direction if all three sensors have been triggered and in a "wave" motion by comparing times
			if (self.timeOn[0] <= self.timeOn[1] <= self.timeOn[2]): # Interval comparison
				self.waves += 1
				#print(f"New Wave: {self.waves}")
				#print("Direction: Positive")
				self.direction()
				self.speed()
				#print(f"Speed: {self.dir*self.spd}")
				self.triggered = [False for i in range(0,len(self.triggered))]
			if (self.timeOn[0] >= self.timeOn[1] >= self.timeOn[2]):
				self.waves += 1
				#print(f"New Wave: {self.waves}")
				#print("Direction: Negative")
				self.direction()
				self.speed()
				#print(f"Speed: {self.dir*self.spd}")
				self.triggered = [False for i in range(0,len(self.triggered))]


	def stop(self):
		for sensor in self.vl53:
			sensor.stop_continuous() # Implemenet error handling if other functions are called while continuous ranging is off


if __name__ == '__main__':
	import board
	import busio
	print("Initializing")
	#Initiliaze I2C
	i2c = board.I2C()
	pins = [9,11,0] # Pins for Shutoff pins
	GPIO.setmode(GPIO.BCM)
	for pin in pins:
			print(pin, "Setup")
			GPIO.setup(pin, GPIO.OUT)
			GPIO.output(pin,GPIO.LOW)
	wave = Gesture(pins,i2c)
	try:
		while True:
			print("------ New Wave --------")
			wave.update()
			print(f"Positions: {wave.pos}")
			print(f"Time: {wave.time}")
			print(f"Speed: {wave.dir*wave.spd}")	
			print(f"Waves: {wave.waves}")	
			print("----------------")		
			sleep(1)
	except KeyboardInterrupt:
		wave.stop()
		GPIO.cleanup()
		i2c.unlock()
		print("Program Terminated by User.")
