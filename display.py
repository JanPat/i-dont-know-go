"""
This file contains a function to display text on the OLED
"""
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import ST7735
import time

#OLED display to host the user interface
#inputs an array to display on the screen
class OLED:
	def display(text):
		disp = ST7735.ST7735(port=0, cs=0, dc=24, backlight=None, rst=25, width=128, height=160, rotation=0, invert=False) 
		WIDTH = 128
		HEIGHT = 128
		offset = 5
		img = Image.new('RGB', (WIDTH, HEIGHT))
		draw = ImageDraw.Draw(img)

		# Load default font.
		font = ImageFont.load_default()

		for element in text:
			draw.text((5, offset),str(element) , font=font, fill=(255, 255, 255))
			offset+=10
		
		disp.display(img) 
