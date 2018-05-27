from . import PyTrackBuffer

defaultNumOfChannels=2

def ObjectToId(obj):
	'''
	Utility only used intenally. User don't use it.
	'''
	if type(obj) is list:
		return [ObjectToId(sub_obj) for sub_obj in obj]
	else:
		return obj.id

class TrackBuffer:
	'''
	Basic data structure storing waveform.
	The content can either be generated by "play" and "sing" calls or by mixing track-buffer into a new one
	'''
	def __init__ (self, chn=-1):
		'''
		chn is the number of channels, which can be 1 or 2
		'''
		if chn==-1:
			chn=defaultNumOfChannels
		if chn<1:
			chn=1
		elif chn>2:
			chn=2
		self.id= PyTrackBuffer.InitTrackBuffer(chn)

	def __del__(self):
		PyTrackBuffer.DelTrackBuffer(self.id)

	def setVolume(self,volume):
		'''
		Set the volume of the track. This value is used as a weight when mixing tracks.
		volume -- a float value, in range [0.0,1.0]
		'''
		PyTrackBuffer.TrackBufferSetVolume(self.id, volume)

	def getVolume(self):
		'''
		Get the volume of the track. This value is used as a weight when mixing tracks.
		Returned value is a float
		'''
		return PyTrackBuffer.TrackBufferGetVolume(self.id)

	def setPan(self, pan):
		'''
		Set the panning of the track. This value is used when mixing tracks.
		pan -- a float value, in range [-1.0,1.0]
		'''
		PyTrackBuffer.TrackBufferSetPan(self.id, pan)

	def getPan(self):
		'''
		Get the panning of the track. This value is used when mixing tracks.
		Returned value is a float
		'''
		return PyTrackBuffer.TrackBufferGetPan(self.id)

	def getNumberOfSamples(self):
		'''
		Get the number of PCM samples of the buffer.
		Returned value is an integer
		'''
		return PyTrackBuffer.TrackBufferGetNumberOfSamples(self.id)

	def getNumberOfChannles(self):
		'''
		Get the number of Channels of the buffer.
		Returned value is an integer
		'''
		return PyTrackBuffer.TrackBufferGetNumberOfChannels(self.id)

	def getAlignPosition(self):
		'''
		Get the align position of the buffer
		The postion will be used as the logical original point when mixed with other track buffers
		The unit is in number of samples
		Returned value is an integer 
		'''
		return PyTrackBuffer.TrackBufferGetAlignPos(self.id)

	def getCursor(self):
		'''
		Get the cursor position of the buffer.
		The unit is in milliseconds.
		Returned value is a float
		'''
		return PyTrackBuffer.TrackBufferGetCursor(self.id)

	def setCursor(self, cursor):
		'''
		Set the curosr position of the buffer.
		The unit is in milliseconds.
		cursor -- a float value, cursor >= 0.0
		'''
		PyTrackBuffer.TrackBufferSetCursor(self.id, cursor)

	def moveCursor(self, cursor_delta):
		'''
		Set the curosr position of the buffer to current position + cursor_delta.
		The unit is in milliseconds.
		cursor_delta -- a float value
		'''
		PyTrackBuffer.TrackBufferMoveCursor(self.id, cursor_delta)

	def writeBlend(self, wavBuf):
		'''
		Write and blend a wavBuf (returned from GenerateSentence for example)
		into current trackbuffer. Cursor will not be moved. Need another call to 
		move the cursor.
		'''
		PyTrackBuffer.TrackBufferWriteBlend(self.id, wavBuf)


def MixTrackBufferList (targetbuf, bufferList):
	'''
	Function used to mix a list of track-buffers into another one
	targetbuf -- an instance of TrackBuffer to contain the result
	bufferList -- a list a track-buffers
	'''
	PyTrackBuffer.MixTrackBufferList(targetbuf.id, ObjectToId(bufferList))

def WriteTrackBufferToWav(buf, filename):
	'''
	Function used to write a track-buffer to a .wav file.
	buf -- an instance of TrackBuffer
	filename -- a string
	'''
	PyTrackBuffer.WriteTrackBufferToWav(buf.id, filename)

def ReadTrackBufferFromWav(buf, filename):
	'''
	Function used to read a track-buffer from a .wav file.
	buf -- an instance of TrackBuffer
	filename -- a string
	'''
	PyTrackBuffer.ReadTrackBufferFromWav(buf.id, filename)

