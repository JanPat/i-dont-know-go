"""
This file contains a function to get the coordinates from the GPS 
"""
import serial
import time
import string
import pynmea2

#GPS gets coordinates
#UART communication protocols
def getCoordinates():
	port="/dev/ttyAMA0"
	ser=serial.Serial(port, baudrate=9600, timeout=0.5)
	dataout = pynmea2.NMEAStreamReader()
	newdata=ser.readline()

	if newdata[0:6] == "$GPRMC":
		newmsg=pynmea2.parse(newdata)
		lat=newmsg.latitude
		lng=newmsg.longitude
		gps = [lat,lng] 
		return gps
