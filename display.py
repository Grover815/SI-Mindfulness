# display.py
from PIL import Image, ImageDraw, ImageFont
from logs import setup_logger

class DisplayGUI():

	# Initialize disp object from adafruit library, pass disp object from main
	def __init__(self,display,connection):
		self.disp = display
		self.width = display.width
		self.height = display.height
		self.conn = connection


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
		text = messages[int(message)].split('\n')
		for i in text:
	
			bbox = font.getbbox(i)
			(font_width, font_height) = bbox[2] - bbox[0], bbox[3] - bbox[1]
			draw.text( (width // 2 - font_width // 2, height // 2 - font_height*(len(text)-text.index(i))//2+5*text.index(i)),i,font=font,fill = 255)
		
		#display image
		self.disp.image(image)
		self.disp.show()

		
	def write(self,message):
		logger = setup_logger()
		logger.info(f"Write message: {message}")
		
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
		draw.text((0,0),message,font=font,fill = 255)
		
		#display image
		self.disp.image(image)
		self.disp.show()
	
	# Multiprocess implementation of writeMessage() and write()
	def message(self):
		logger = setup_logger()
		logger.info(f"{current_process().name} running...")
		while True:
			if self.conn.poll():
				msg = self.conn.recv()
				logger.info(f"{current_process().name} Received: {msg}")
				text = None
				if type(msg) == int:

					'''Takes in one of our mindfullness messages and displays it indefinately'''
					messages = ["Resistance makes\nsuccess worthwhile.","I am capablre of\nsuccedding.","This too shall pass.","Everything is as it\nis.",
					"Quiet the mind and\nthe soul will speak.",
					"My grades do not\ndefine me."]
					text = messages[int(msg)].split('\n')
				if type(msg) == str:
					text=msg.split('\n')
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
				
				for i in text:
				
					bbox = font.getbbox(i)
					(font_width, font_height) = bbox[2] - bbox[0], bbox[3] - bbox[1]
					draw.text( (width // 2 - font_width // 2, height // 2 - font_height*(len(text)-text.index(i))//2+5*text.index(i)),i,font=font,fill = 255)
				
				#display image
				self.disp.image(image)
				self.disp.show()


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

if __name__ == '__main__':
	import board
	import busio
	import adafruit_ssd1306
	i2c = busio.I2C(board.SCL,board.SDA)
	disp = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c,addr=0x3d)
	GUI = DisplayGUI(disp)
	GUI.writeMessage(0)
