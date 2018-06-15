#!/usr/bin/env python
import sys
import time
import numpy as np
import serial 

class SHT30(object):
	def __init__(self, serial_address):
		self._temperature		= 0
		self._temperature_crc	= 0
		self._humidity			= 0
		self._humidity_crc		= 0
		self._ser = serial.Serial(serial_address, baudrate = 115200)

	def _crc_calc(self, value):
		# Initialize with parameters from datasheet
		polynomial = 0x31
		crc8 = 0xFF

		# Split value into 2 bytes
		values = [ (value >> 8) & 0xFF, value & 0xFF ]

		# Calculate CRC for both bytes
		for byte in values:
			crc8 ^= byte

			for i in range(0,8):
				if crc8 & 0x80 != 0:
					crc8 = ((crc8 << 1) ^ polynomial) & 0xFF
				else:
					crc8 = crc8 << 1

		return np.uint8(crc8)

	# Single function to update temperature, humidity and write to PIC
	# Inputs are decimal values for T/H and temperature units, as a character
	def set_temp_humidity(self, temp, hum, units = 'F'):
		# Set temperature (check units)
		if units.lower() == 'f':
			self._set_temperature_F(temp)
		elif units.lower() == 'c':
			self._set_temperature_C(temp)
		else:
			print "Invalid units selection: %s" % units
			return False

		# Set humidity
		self._set_humidity(hum)

		# Write new temperature and humidity
		self._write_to_pic()

		return True


	def _write_to_pic(self):
		# Convert temps and hums to bytes
		tempMSB = (self._temperature >> 8) & 0xFF
		tempLSB = self._temperature & 0xFF
		humMSB  = (self._humidity >> 8) & 0xFF
		humLSB  = self._humidity & 0xFF
		
		# Array of bytes to transmit
		tx_buff = bytearray([int(tempMSB), int(tempLSB), 
			                 int(self._temperature_crc), 
			                 int(humMSB),  int(humLSB),  
			                 int(self._humidity_crc)])

		# Write buffer to serial
		self._ser.write(tx_buff)

		# Debug output
		#print "Sent to PIC:          %X %X %X %X %X %X" %(tx_buff[0], tx_buff[1], tx_buff[2],
		#										 		  tx_buff[3], tx_buff[4], tx_buff[5],)
	
	def _set_temperature_F(self, temp):
		# Formula from datasheet (trim to 16-bit value)
		self._temperature = np.uint16(((temp + 49.0)*65535.0)/315.0) & 0xFFFF
		# Calculate CRC
		self._temperature_crc = self._crc_calc(self._temperature)

		# Debug output
		#print "Temperature data (F): %X | CRC: %X" % (self._temperature, self._temperature_crc)
		
	def _set_temperature_C(self, temp):
		# Formula from datasheet (trim to 16-bit value)
		self._temperature = np.uint16(((temp + 45.0)*65535.0)/175.0) & 0xFFFF
		# Calculate CRC
		self._temperature_crc = self._crc_calc(self._temperature)

		# Debug output
		#print "Temperature data (C): %X | CRC: %X" % (self._temperature, self._temperature_crc)

	def _set_humidity(self, hum):
		# Check range
		if hum < 0:
			hum = 0
		elif hum > 100:
			hum = 100
		# Formula from datasheet (trim to 16-bit value)
		self._humidity = np.uint16((hum*65535.0)/100.0) & 0xFFFF
		# Calculate CRC
		self._humidity_crc = self._crc_calc(self._humidity)

		# Debug output
		#print "Humidity data (RH):   %X | CRC: %X" % (self._humidity, self._humidity_crc)
		

	

