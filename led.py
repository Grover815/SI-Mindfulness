# led.py

import RPi.GPIO as GPIO
from time import sleep
#import random

class Led:

	def __init__(self,pin):
		self.pin = pin
		self.brightness = 100 # 0-100 exclusive mapped to duty cycle
		self.red_pin = 26
		self.green_pin = 19
		self.blue_pin = 13
		#GPIO.setup(pin, GPIO.OUT) # LED PIN number
		self.pwm = GPIO.PWM(pin,1000)
		GPIO.setup(self.red_pin, GPIO.OUT) #R
		GPIO.setup(self.green_pin, GPIO.OUT) #G
		GPIO.setup(self.blue_pin, GPIO.OUT) #B

	def red(self):
		GPIO.output(self.red_pin, GPIO.HIGH)

	def blue(self):
		GPIO.output(self.blue_pin, GPIO.HIGH)

	def green(self):
		GPIO.output(self.green_pin, GPIO.HIGH)
	
	def coloroff(self):
		GPIO.output(self.green_pin, GPIO.LOW)
		GPIO.output(self.blue_pin, GPIO.LOW)
		GPIO.output(self.red_pin, GPIO.LOW)

	def on(self, color, DC):
		if color == 'G':
			self.green()
		if color == 'B':
			self.blue()
		if color == 'R':
			self.red()
		self.pwm.start(DC)

	def off(self):
		self.coloroff()
		self.pwm.stop()

	def breath(self, color):
		if color == 'G':
			self.green()
		if color == 'B':
			self.blue()
		if color == 'R':
			self.red()
		self.pwm.start(0)
		for i in range(0,1000):
			DC = i/10
			self.pwm.ChangeDutyCycle(DC)
			sleep(0.001)
		for i in range(0,1000):
			DC = 100 - (i/10)
			self.pwm.ChangeDutyCycle(DC)
			sleep(0.001)
		self.pwm.stop()
		self.coloroff()

class ColorGroup:
# DO I NEED TO DO BCM MODE SETUP
	def __init__(self, leds): # Takes list of LED instances
		self.leds = leds
	'''
		self.red_pin = 2
		self.green_pin = 3
		self.blue_pin = 4
		GPIO.setup(self.red_pin, GPIO.OUT) #R
		GPIO.setup(self.green_pin, GPIO.OUT) #G
		GPIO.setup(self.blue_pin, GPIO.OUT) #B
	
	def red(self):
		GPIO.output(self.red_pin, GPIO.HIGH)

	def blue(self):
		GPIO.output(self.blue_pin, GPIO.HIGH)

	def green(self):
		GPIO.output(self.green_pin, GPIO.HIGH)

	def coloroff(self):
		GPIO.output(green_pin, GPIO.LOW)
		GPIO.output(blue_pin, GPIO.LOW)
		GPIO.output(red_pin, GPIO.LOW)
	'''
	def pattern(self, color, position):
		color = color 
		if all(x == 0 for x in position):
			hold = False
			return hold
		else:
			hold = True
			for i in range(len(self.leds)):
				DC = 0
				if i % 2 == 0:
					if position[i//2]:
						DC = 100
					else:
						DC = 0
				else:
					if position[(i-1)//2] or position[(i+1)//2]:
						DC = 7
					else:
						DC = 0
				self.leds[i].on(color, DC)
			sleep(0.1)
			for i in self.leds:
				i.off()
			return hold
'''	
	def holdpattern(self, start):
		if time.time() - start >= 5:
			for i in range(0,10):
				for i in self.leds:
					self.leds[i].on(R, 100)
				sleep(0.5)
				self.coloroff()
				for i in self.leds:
					self.leds[i].on(G, 100)
				sleep(0.5)
				self.coloroff()
				for i in self.leds:
					self.leds[i].on(B, 100)
				sleep(0.5)
				self.coloroff()
		else:
			return
'''

##pins = [] # Pins for Shutoff pins
##ledpins = [] # LED power pins for sensor LEDS
##LED_instance = []
##colors = ['R', 'G', 'B']
##
##wave = Gesture(pins,i2c)
##for i in ledpins:
##	LED_instance.append(Led(i))
##
##SensorLeds = ColorGroup(LED_instance)
##
##try:
##	t = time.time()
##	while True:
##		randcolor = random.choice(colors)
##		wave.update()
##		pos = wave.position()
##		hold = SensorLeds.pattern(randcolor, pos)
##		if hold:
##			SensorLeds.holdpattern(hold, t)
##		else:
##			t = time.time()
##	except KeyboardInterrupt:
##		wave.stop()
##		GPIO.cleanup()
##		print("Program Terminated by User.")
if __name__ == "__main__":
	from distance import Gesture
	GPIO.cleanup()
	led_pins = [14, 15, 18, 23, 24]
	LEDS = []
	for i in led_pins:
	        LEDS.append(Led(i))

	sensor_LEDS = ColorGroup(LEDS)
	pos = [0,0,1]
	sensor_LEDS.pattern('B', pos)

	##for j in LEDS:
	##        j.on("R", 100)
	##        sleep(1)
	##for j in LEDS:
	##        j.off()
	        
	print("All done.")


		





