class VideoStream:
	def __init__(self, filename):
		self.filename = filename
		try:
			self.file = open(filename, 'rb')
		except:
			raise IOError
		self.frameNum = 0
		
	def nextFrame(self):
		"""Get next frame."""
		data = self.file.read(5) # Get the framelength from the first 5 bits
		if data: 
			framelength = int(data)
							
			# Read the current frame
			data = self.file.read(framelength)							
			self.frameNum += 1
		return data
		
	def frameNbr(self):
		"""Get frame number."""
		return self.frameNum

	def getVideoInfo(self):
		import cv2
		cv2video = cv2.VideoCapture(self.filename)
		#Get size of Video frame:
		height = cv2video.get(cv2.CAP_PROP_FRAME_HEIGHT)
		width  = cv2video.get(cv2.CAP_PROP_FRAME_WIDTH) 
		#GetDuration of video
		framecount = self.count_frames_manual(cv2video)
		frames_per_sec = cv2video.get(cv2.CAP_PROP_FPS)
		videoDuration = framecount / frames_per_sec
		#Get Video encoding:
		videoEncode = cv2video.getBackendName()
		#Result:
		fileInfo = "Size: {}x{}, Video duration: {}, Encode: {}".format(height, \
																		width, \
																		videoDuration, 
																		videoEncode)
		return fileInfo

	def count_frames_manual(self, video):
		total = 0
		while True:
			(grabbed, frame) = video.read()
			# check to see if we have reached the end of the video
			if not grabbed:
				break
			total += 1
		return total
	
	