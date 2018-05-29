#Library for communication with Zeit Devices
#Date: 23-05-18
#Author: LM

import serial
import time

class SerialCommandResponse:
	Success = False
	Data = []
	Message = ""

class SerialPortSettings:
	def __init__(self,port):
		self.port = port
		self.baudrate=9600
		self.parity=serial.PARITY_NONE
		self.stopbits=serial.STOPBITS_TWO
		self.bytesize=serial.EIGHTBITS



class ZeitLEDBoard:
	SendPingCommandID=1
	UpdateDisplayCommandID=4
	GetStatusCommandID=5


	def __init__(self,serialPortSettings,retries,timeout,printDebugLines):
		self.serialPortSettings = serialPortSettings
		self.retries=retries
		self.timeout=timeout
		self.debug = printDebugLines

	def SendPing(self,DisplayID):
		values = bytearray([47, 84, 71, DisplayID, ZeitLEDboard.SendPingCommandID, 0, 92])
		checksum = self.__calculateChecksum(values[1:5])
		values[5]=checksum
		return self.__SendData(self.serialPortSettings,ZeitLEDboard.SendPingCommandID,values)
	
	def UpdateDisplay(self,DisplayID,Value,Decimals):
		values = bytearray([47, 84, 71, DisplayID, ZeitLEDboard.UpdateDisplayCommandID, 48,48,48,48,48,48,48,48,48,48,48,48,48,48,48,48,Value,Decimals,0,92])
		checksum = self.__calculateChecksum(values[1:23])
		values[23]=checksum
		return self.__SendData(self.serialPortSettings,ZeitLEDboard.UpdateDisplayCommandID,values)

	def GetStatus(self,DisplayID):
		values = bytearray([47, 84, 71, DisplayID, ZeitLEDboard.GetStatusCommandID, 0, 92])
		checksum = self.__calculateChecksum(values[1:5])
		values[5]=checksum
		return self.__SendData(self.serialPortSettings,ZeitLEDboard.GetStatusCommandID,values)
	
	def __calculateChecksum(self,BytesArray):
		checksum=0
		for byte in BytesArray:
			checksum^=byte
		return checksum

	def __ValidateAck(self,CommandID,Data):
		srlResponse = SerialCommandResponse()
		if(CommandID == ZeitLEDboard.SendPingCommandID):
			#print 'Validating Command ID: ' + str(CommandID) + ' Data Lenght: ' + str(len(Data))
			if(len(Data)>=8):
				#print Data
				if(Data[0]=='/' and Data[1]=='t' and Data[2]=='g' and Data[4]==chr(CommandID) and Data[7]=='\\'):
					srlResponse.Success=True
					srlResponse.Data = Data[5:6]
		elif(CommandID == ZeitLEDboard.UpdateDisplayCommandID):
			#print 'Validating Command ID: ' + str(CommandID) + ' Data Lenght: ' + str(len(Data))
			if(len(Data)>=8):
				if(Data[0]=='/' and Data[1]=='t' and Data[2]=='g' and Data[4]==chr(CommandID) and Data[7]=='\\'):
					srlResponse.Success=True
					srlResponse.Data = Data[5:6]
		elif(CommandID == ZeitLEDboard.GetStatusCommandID):
			#print 'Validating Command ID: ' + str(CommandID) + ' Data Lenght: ' + str(len(Data))
			if(len(Data)>=9):
				if(Data[0]=='/' and Data[1]=='t' and Data[2]=='g' and Data[4]==chr(CommandID) and Data[8]=='\\'):
					srlResponse.Success=True
					srlResponse.Data = Data[5:7]
		return srlResponse

	def __SendData(self,serialPortSettings,CommandID,Data):
		try:
			ser = serial.Serial(
				port=serialPortSettings.port,
				baudrate=serialPortSettings.baudrate,
				parity=serialPortSettings.parity,
				stopbits=serialPortSettings.stopbits,
				bytesize=serialPortSettings.bytesize
			)
			if(ser.isOpen() == False):
				ser.open()
			tries=0
			srlResponse = SerialCommandResponse()
			while((tries<self.retries) and (srlResponse.Success == False)):
				if(self.debug):
					print "Send Data: "
					for byte in Data:
						print byte,
				ser.write(Data)
				time.sleep(self.timeout)
				dataReceived = ''
				while ser.inWaiting() > 0:
					dataReceived += ser.read(1)
				
				if(len(dataReceived)!= 0):
					#print "Data Received: " + dataReceived 
					srlResponse=self.__ValidateAck(CommandID,dataReceived)
				tries +=1
			
			ser.close()
			return srlResponse
		except IOError:
			ser.close()
			ser.open()
			print 'Port was open, was closed and opened again'