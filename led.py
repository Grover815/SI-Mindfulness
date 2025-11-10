# led.py

import RPi.GPIO as GPIO
from time import sleep

class Led:

	def __init__(self,pin):
		self.pin = pin
		self.brightness = 0 # 0-100 exclusive mapped to duty cycle

	def on(self):
		pwm = GPIO.PWM(self.pin,1000)
		pwm.start(self.brightness)
		sleep(1)
		pwm.stop()


	def breath(self):
		pass



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


