class VideoStream:
	def __init__(self, filename):
		self.filename = filename
		try:
			self.file = open(filename, 'rb')
			print('-'*60 +  "\nVideo file : |" + filename +  "| read\n" + '-'*60)
		except:
			raise IOError
		self.frameNum = 0

	def nextFrame(self):
		"""Get next frame."""
		data = self.file.read(5) # Get the framelength from the first 5 bytes
		data = bytearray(data)

		if data:
			framelength = int(data)
			
			# Read the current frame
			frame = self.file.read(framelength)
			if len(frame) != framelength:
				raise ValueError('incomplete frame data')
			self.frameNum += 1
			return frame

	def frameNbr(self):
		"""Get frame number."""
		return self.frameNum

