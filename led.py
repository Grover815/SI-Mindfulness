# led.py

import RPi.GPIO as GPIO
from time import sleep

class Led:

	def __init__(self,pin):
		self.pin = pin
		self.brightness = 100 # 0-100 exclusive mapped to duty cycle
		self.red_pin = 2
		self.green_pin = 3
		self.blue_pin = 4
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(pin, GPIO.OUT) # LED PIN number
		GPIO.setup(self.red_pin, GPIO.OUT) #R
		GPIO.setup(self.green_pin, GPIO.OUT) #G
		GPIO.setup(self.blue_pin, GPIO.OUT) #B

	def red(self):
		GPIO.output(self.red_pin, GPIO.HIGH)

	def blue(self):
		GPIO.output(self.blue_pin, GPIO.HIGH)

	def green(self):
		GPIO.output(self.green_pin, GPIO.HIGH)
	
	def coloroff():
		GPIO.output(green_pin, GPIO.LOW)
		GPIO.output(blue_pin, GPIO.LOW)
		GPIO.output(red_pin, GPIO.LOW)

	def on(self, color, secs):
		if color == 'G':
			self.green()
		if color == 'B':
			self.blue()
		if color == 'R':
			self.red()
		pwm = GPIO.PWM(self.pin,1000)
		pwm.start(self.brightness)
		sleep(secs)
		pwm.stop()
		self.coloroff()

	def breath(self, color):
		if color == 'G':
			self.green()
		if color == 'B':
			self.blue()
		if color == 'R':
			self.red()
		pwm = GPIO.PWM(self.pin,1000)
		pwm.start(0)
		for i in range(0,1000):
			DC = i/10
			pwm.ChangeDutyCycle(DC)
			sleep(0.001)
		for i in range(0,1000):
			DC = 100 - (i/10)
			pwm.ChangeDutyCycle(DC)
			sleep(0.001)
		pwm.stop()
		self.coloroff()


if __name__ == '__main__':
	print("~LED Test~")
	n = input("How many LED's are you testing?: ")
	leds = []
	for i in range(0,len(pins)):
		pin = input(f"Pin {i+1}?: ")
		leds.append(Led(pin))
	for led in leds:
		led.on(50)
		sleep(1)


