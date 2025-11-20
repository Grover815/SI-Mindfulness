# display.py
from PIL import Image, ImageDraw, ImageFont
import time
import board
import busio
import adafruit_ssd1306

class DisplayGUI():

	# Initialize disp object from adafruit library, pass disp object from main
	def __init__(self,display):
		self.disp = display
		self.width = display.width
		self.height = display.height


	# Function to write message
	def writeMessage(self,message):
		'''Takes in one of our mindfullness messages and displays it indefinately'''
		messages = ["Resistance makes\nsuccess worthwhile.","I am capablre of\nsuccedding.","This too shall pass.","Everything is as it\nis.",
		"Quiet the mind and\nthe soul will speak.",
		"My grades do not\ndefine me."]
		# Clear display.
		self.disp.fill(0)
		self.disp.show()

		# Create blank image for drawing.
		# Make sure to create image with mode '1' for 1-bit color.
		width = self.disp.width
		height = self.disp.height
		image = Image.new("1", (width, height))

		# Get drawing object to draw on image.
		draw = ImageDraw.Draw(image)
		#import font
		font = ImageFont.load_default()
		#define starting position


		# Draw a black filled box to clear the image.
		draw.rectangle((0, 0, width, height), outline=0, fill=0)
		draw.text((0,0),messages[message],font=font,fill = 255)
		
		#display image
		self.disp.image(image)
		self.disp.show()
                time.sleep(0.1)

		

	

	def showStats(self,stats):
		'''Takes in a list of stats such as total RPM's, cycle time, max speed, etc 
		and displays the stats at the end of each useage'''
		# Clear display.
		self.disp.fill(0)
		self.disp.show()

		# Create blank image for drawing.
		# Make sure to create image with mode '1' for 1-bit color.
		width = self.disp.width
		height = self.disp.height
		image = Image.new("1", (width, height))

		# Get drawing object to draw on image.
		draw = ImageDraw.Draw(image)
		#import font
		font = ImageFont.load_default()
		#define height
		height = 32*self.height//len(stats)
                draw.rectangle((0, 0, width, height), outline=0, fill=0)

		for i in range(len(stats)):
			# Draw a black filled box to clear the image.
			
			draw.text((0,i*height),stats[i],font=font,fill = 255)
			
		#display image
		self.disp.image(image)
		self.disp.show()
		time.sleep(0.1)
if __name__ == 'main':
	i2c = busio.I2C(board.SCL,board.SDA)
	disp = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)
	GUI = DisplayGUI(disp)
	GUI.writeMessage('Hello World!')
