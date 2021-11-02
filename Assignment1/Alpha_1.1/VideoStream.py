BACKWARD = 0
FORWARD = 1

class VideoStream:
	def __init__(self, filename):
		self.filename = filename
		try:
			self.file = open(filename, 'rb')
		except:
			raise IOError
		self.trackFrameList = self.trackFrame()		
		self.frameNum = 0
		self.height = None
		self.width = None
		self.videoTotalFrame = None
		self.frames_per_sec = None
		self.videoDuration = None
		self.videoEncode = None
		self.initVideoInfo()
		
		
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

	#type = 0 is backward
	#type = 1 is forward
	def setFrame(self, seconds = 0, type=FORWARD):
		"""Set frame number"""
		frames = int(seconds / self.videoDuration * self.videoTotalFrame)
		print("frames: {}".format(frames) )
		if (type == BACKWARD):
			self.frameNum = max(0, self.frameNum - frames)
			self.file.seek(self.trackFrameList[self.frameNum], 0)
			
		else:
			self.frameNum = min(self.videoTotalFrame, self.frameNum + frames)
			self.file.seek(self.trackFrameList[self.frameNum], 0)
				

	def initVideoInfo(self):
		import cv2
		cv2video = cv2.VideoCapture(self.filename)
		self.height = cv2video.get(cv2.CAP_PROP_FRAME_HEIGHT)
		self.width  = cv2video.get(cv2.CAP_PROP_FRAME_WIDTH) 
		self.frames_per_sec = cv2video.get(cv2.CAP_PROP_FPS)
		self.videoTotalFrame = self.count_frames_manual(cv2video)
		self.videoEncode = cv2video.getBackendName()
		self.videoDuration = self.videoTotalFrame / self.frames_per_sec

	def trackFrame(self):
		trackFrameList = []
		while True:
			trackFrameList.append(self.file.tell())
			data = self.file.read(5) # Get the framelength from the first 5 bits
			if data: 
				framelength = int(data)
				# Read the current frame
				data = self.file.read(framelength)					
			else: #End of file
				break
		self.file.seek(0)
		return trackFrameList
				

	def getVideoInfo(self):																
		return "{}x{}\n{}\n{}\n{}\n{}".format(self.height, \
											self.width, \
											self.videoDuration, \
											self.videoEncode, \
											self.videoTotalFrame, \
											self.frames_per_sec)

	def count_frames_manual(self, video):
		total = 0
		while True:
			(grabbed, frame) = video.read()
			# check to see if we have reached the end of the video
			if not grabbed:
				break
			total += 1
		return total
	
	