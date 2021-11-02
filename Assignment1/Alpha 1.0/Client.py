from time import sleep
from tkinter import *
from time import time
import tkinter.messagebox
from PIL import Image, ImageTk,ImageFile
import socket, threading, sys, traceback, os
ImageFile.LOAD_TRUNCATED_IMAGES = True
from RtpPacket import RtpPacket
from VideoStream import VideoStream
from RtspPacket import PAUSE, TEARDOWN, RtspPacket
from io import BytesIO

CACHE_FILE_NAME = "cache-"
CACHE_FILE_EXT = ".jpg"

FRAME_HEADER_LENGTH = 5
DEFAULT_IMAGE_SHAPE = (380, 280)
VIDEO_LENGTH = 500
DEFAULT_FPS = 24

# if it's present at the end of chunk,
# it's the last chunk for current jpeg (end of frame)
JPEG_EOF = b'\xff\xd9'

class Client:
	DEFAULT_LOCAL_HOST = '127.0.0.1'
	INIT = 0
	READY = 1
	PLAYING = 2
	# SWITCH = 7
	
	SETUP = 0
	PLAY = 1
	PAUSE = 2
	TEARDOWN = 3
	DESCRIBE = 4
	FORWARD5SECONDS = 5
	BACKWARD5SECONDS = 6
	SWITCH = 7

	state = INIT
	DEFAULT_TIME_CLOCK = 50 # 50ms
	
	# Initiation..
	def __init__(self, master, serveraddr, serverport, rtpport, filename):
		self.master = master	# screen
		self.master.protocol("WM_DELETE_WINDOW", self.handler) # Click 'x' button automatically call self.handler()
		self.createWidgets()
		self.serverAddr = serveraddr
		self.serverPort = int(serverport)
		self.rtpPort = int(rtpport)
		self.fileName = filename
		self.rtspSeq = 0
		self.sessionId = 0																																					
		self.frameNbr = 0
		self.frameCurrent = 0
		self.frameLoss = 0
		
		self.rtspSocket = None
		self.isRtpThreadStopped = False
		self.isVideoThreadStopped = False
		self.isRtspSocketCreated = False
		self.rtpSocket = None
		self.rtpThread = None
		self.isReceivingRtp = False
		self.frame_buffer = []
		self.videoDataRate = []
		self.currentFrameInstalledIndex = -1
		self.currentFrameDisplayedIndex = 0
		self.timeStampPrev = 0
		self.timeStampCur = 0
		self.connectToServer()

		self.videoPlayerThread = None

		#Attribute for video information:
		self.videoTotalFrame = None
		self.videoEncode = None
		self.videoDuration = None
		self.videoFps = None
		self.videoFrameSize = None

	# THIS GUI IS JUST FOR REFERENCE ONLY, STUDENTS HAVE TO CREATE THEIR OWN GUI 	
	def createWidgets(self):
		"""Build GUI."""
		# Create Setup button
		self.setup = Button(self.master, width=20, padx=3, pady=3)
		self.setup["text"] = "Setup"
		self.setup["command"] = self.setupMovie
		self.setup.grid(row=1, column=0, padx=2, pady=2)
		
		# Create Play button		
		self.start = Button(self.master, width=20, padx=3, pady=3)
		self.start["text"] = "Play"
		self.start["command"] = self.playMovie
		self.start.grid(row=1, column=1, padx=2, pady=2)
		
		# Create Pause button			
		self.pause = Button(self.master, width=20, padx=3, pady=3)
		self.pause["text"] = "Pause"
		self.pause["command"] = self.pauseMovie
		self.pause.grid(row=1, column=2, padx=2, pady=2)
		
		# Create Teardown button
		self.teardown = Button(self.master, width=20, padx=3, pady=3)
		self.teardown["text"] = "Teardown"
		self.teardown["command"] =  self.exitClient
		self.teardown.grid(row=1, column=3, padx=2, pady=2)

		# Create Describe button
		self.describe = Button(self.master, width=20, padx=3, pady=3)
		self.describe["text"] = "Describe"
		self.describe["command"] =  self.describeMovie
		self.describe.grid(row=1, column=4, padx=2, pady=2)

		# Create Forward 5s button
		self.forward = Button(self.master, width=20, padx=3, pady=3)
		self.forward["text"] = "Forward 5s"
		self.forward["command"] =  self.forward5seconds
		self.forward.grid(row=1, column=5, padx=2, pady=2)

		# Create Forward 5s button
		self.backward = Button(self.master, width=20, padx=3, pady=3)
		self.backward["text"] = "Backward 5s"
		self.backward["command"] =  self.backward5seconds
		self.backward.grid(row=1, column=6, padx=2, pady=2)

		# Create Switch button
		self.backward = Button(self.master, width=20, padx=3, pady=3)
		self.backward["text"] = "Switch"
		self.backward["command"] =  self.switchMovie
		self.backward.grid(row=1, column=7, padx=2, pady=2)
		
		# Create a label to display the movie
		self.label = Label(self.master, height=19)
		self.label.grid(row=0, column=0, columnspan=4, sticky=W+E+N+S, padx=5, pady=5) 
	
	def setupMovie(self):
		"""Setup button handler. Starting RTP receiving thread"""
		if self.state == self.INIT:
			self.isRtpThreadStopped = False
			self.isVideoThreadStopped = False
			self.openRtpPort()
			#Set up movie:
			request = RtspPacket(self.SETUP, self.fileName, self.rtspSeq, self.rtpPort).generate()
			response = self.sendRtspRequest(request)
			self.state = self.READY
			# Reset Display, Install and Measure variables 
			self.currentFrameInstalledIndex = 0
			self.currentFrameDisplayedIndex = 0
			self.timeStampPrev = 0
			self.timeStampCur = 0																					
			self.frameNbr = 0
			self.frameCurrent = 0
			self.frameLoss = 0
			self.frame_buffer = []
			self.videoDataRate = []

			# Get Video Info
			self.getMovieInfo()
			return response
	#TODO

	def switchMovie(self):	
		if self.state == self.INIT:
			self.playMovie()		
		if self.state != self.READY:
			self.pauseMovie()
		self.state = self.SWITCH
		request = RtspPacket(self.SWITCH, self.fileName, self.rtspSeq, self.rtpPort).generate()
		# To be implemented: server reponse with dictionary containing array of string for each filename 
		response = self.sendRtspRequest(request)
		# Remove empty '' string
		filenameList = list(filter(lambda var : (var != '') ,response[3].split(' ')))
		print("File Name List: ",filenameList)
		# To be implemented: setting up new Tk() open choose menu
		self.chooseFilenameMenuApp(filenameList)

		if self.newFilename == self.fileName:
			# The same movie -> back to normal PAUSE state
			self.state = self.READY
		else:
			# New movie -> TEARDOWN old rtp connection, SETUP new connection with the new filename
			self.fileName = self.newFilename
			self.exitClient()
		# ...
		pass

	
	def chooseFilenameMenuApp(self, filenameList):
		top = Toplevel(self.master)
		# top.protocol("WM_DELETE_WINDOW", top.destroy)
		top.title("Choose filename")
		newFilenameRadioValue = StringVar()
		for filename in filenameList:
			Radiobutton(top, text=filename, value=filename, variable=newFilenameRadioValue, command=newFilenameRadioValue.get()).pack(anchor=W)
		saveButton = Button(top, text="Click to choose this filename", command=lambda: self.saveNewFilenameAndDestroy(newFilenameRadioValue.get(),top))
		saveButton.pack()
		top.wait_window()
		#After destroy mainloop of child TK() objects

	def saveNewFilenameAndDestroy(self, value, top):
		self.newFilename = value
		top.destroy()

	def forward5seconds(self):
		request = RtspPacket(self.FORWARD5SECONDS, self.fileName, self.rtspSeq, self.rtpPort).generate()
		response = self.sendRtspRequest(request)
		self.currentFrameDisplayedIndex = self.currentFrameInstalledIndex
		self.frameNbr = int(self.frameCurrent + (5 * self.videoTotalFrame)/ self.videoDuration)
		if self.frameNbr > self.videoTotalFrame:
			self.frameNbr = self.videoTotalFrame

	def backward5seconds(self):
		request = RtspPacket(self.BACKWARD5SECONDS, self.fileName, self.rtspSeq, self.rtpPort).generate()
		response = self.sendRtspRequest(request)
		self.currentFrameDisplayedIndex = self.currentFrameInstalledIndex
		self.frameNbr = int(self.frameCurrent - (5 * self.videoTotalFrame)/ self.videoDuration) 
		if self.frameNbr < 0:
			self.frameNbr = 0
	
	def exitClient(self):
		"""Teardown button handler."""
		if self.state != self.INIT:
			request = RtspPacket(self.TEARDOWN, self.fileName, self.rtspSeq, self.rtpPort).generate()
			response = self.sendRtspRequest(request)
			print(response[0].split(' ')[1])
			if int(response[0].split(' ')[1]) == 200:
				print("Server closes RTP socket")
			else:
				raise Exception("Teardown message not processed, dangling server rtp socket")
			self.isRtpThreadStopped = True
			self.isVideoThreadStopped = True
			self.videoPlayerThread = None
			self.rtpThread = None
			self.state = self.INIT
			if self.currentFrameInstalledIndex + self.frameLoss != 0:
				loss = (self.frameLoss)/(self.currentFrameInstalledIndex + self.frameLoss)
				print(f"Packet Loss Rate = {loss}")
		# self.handler()
	#TODO																	 

	def pauseMovie(self):
		"""Pause button handler."""
		if self.state == self.READY:
			return
		request = RtspPacket(self.PAUSE, self.fileName, self.rtspSeq, self.rtpPort, self.sessionId).generate()
		response = self.sendRtspRequest(request)
		self.state = self.READY
		return response
	#TODO

	def getMovieInfo(self):
		request = RtspPacket(self.DESCRIBE, self.fileName, self.rtspSeq, self.rtpPort).generate()
		response = self.sendRtspRequest(request)
		self.videoFrameSize = response[1]
		self.videoDuration = float(response[2])
		self.videoTotalFrame = float(response[4])
		self.videoEncode = response[3]
		self.videoFps = float(response[5])
		

	def describeMovie(self):
		#TODO: Show response to UI, you may extract valuable information
		#Get Movie information:
		request = RtspPacket(self.DESCRIBE, self.fileName, self.rtspSeq, self.rtpPort).generate()
		response = self.sendRtspRequest(request)
		print("Total Frame")
		print(self.videoTotalFrame)
		print("Total Duration")
		print(self.videoDuration)
		print("Time remaining")
		print(self.getVideoRemainTime())
		
	
	def playMovie(self):
		"""Play button handler. Trigger server RTP socket sending frame"""
		if self.state == self.INIT:
			self.setupMovie()
		if self.state != self.READY:
			return
		if not self.isReceivingRtp: # prevent multiple similar thread
			self.rtpThread = threading.Thread(target=self.listenRtp, args=(lambda: self.isRtpThreadStopped,))
			self.rtpThread.start()
			self.videoPlayerThread = threading.Thread(target=self.runMovie, args=(lambda: self.isVideoThreadStopped,))
			self.videoPlayerThread.start()
			self.isReceivingRtp = True
		request = RtspPacket(self.PLAY, self.fileName, self.rtspSeq, self.rtpPort, self.sessionId).generate()
		response = self.sendRtspRequest(request)
		self.state = self.PLAYING
		return response
	#TODO
	
	def listenRtp(self, stop):		
		"""Listen for RTP packets."""
		while True:
			# print(f"Is RTP Thread stop(): {stop()}")
			if stop():
				print("Client RTP Thread is safe to terminated")
				self.isReceivingRtp = False
				self.rtpSocket.close()
				break
			if not self.isReceivingRtp:
				sleep(self.DEFAULT_TIME_CLOCK/1000)
				continue
			try: 
				frame_payload = self.recvRTPPacket()
			except TimeoutError:
				sleep(self.DEFAULT_TIME_CLOCK*10/1000)
				continue
			except Exception:
				print("Finish sending or RTP receive failed")
				sleep(self.DEFAULT_TIME_CLOCK*10/1000)
				continue
			frame = Image.open(BytesIO(frame_payload))
			byte = sys.getsizeof(frame.tobytes())
							
			# print(f"Frame imported from rtp: {frame}")
			self.currentFrameInstalledIndex += 1
			self.frame_buffer.append(frame)	

			if self.timeStampPrev != 0:
				videoDataRate = byte * 1000 / (self.timeStampCur - self.timeStampPrev)
				self.videoDataRate.append(videoDataRate)
				print(f"Video Data Rate: {videoDataRate}")
			self.timeStampPrev = self.timeStampCur
	#TODO

	def recvRTPPacket(self):
		bytedata = bytes()
		while True:
			try:
				bytedataPart, addr = self.rtpSocket.recvfrom(4096)
				bytedata += bytedataPart
				if bytedata.endswith(JPEG_EOF):
					break
			except socket.timeout:
				raise TimeoutError("")
		data = RtpPacket()
		data.decode(bytedata)
		if data.seqNum() == 1: # Print first frame of each Mjpeg file (for debugging purpose)
			# print(data.getPayload())
			pass
		self.frameCurrent = data.seqNum()
		self.timeStampCur = int(time() * 1000)
		print(f"Receive frame number: {self.frameNbr}/{self.frameCurrent}")
		return data.getPayload()

					
	def writeFrame(self, data):
		"""Write the received frame to a temp image file. Return the image file."""
		b = BytesIO()
		data.save(b, format="jpeg")
		# print(data)
		return data
	#TODO

	def updateMovie(self, imageFile):
		"""Update the image file as video frame in the GUI."""
		imgTk = ImageTk.PhotoImage(imageFile)
		print(imgTk)
		self.label.config(image=imgTk, width=imgTk.width(), height=imgTk.height())
		self.label.image=imgTk
		# print(self.label.image)
	#TODO
	
	def runMovie(self, stop):
		"""Update the image file as video frame in the GUI."""
		while True:
			sleep(self.DEFAULT_TIME_CLOCK/1000)
			# print(f"Movie Thread stop(): {stop()}")
			if stop():
				print("Movie Player thread is safe to termintate")
				break
			if self.state != self.PLAYING:
				continue
			try:
				if self.frameNbr > self.videoTotalFrame:
					print("Yay")
					self.exitClient()
				img = self.writeFrame(self.frame_buffer[self.currentFrameDisplayedIndex])
				self.updateMovie(img)
				
				self.frameNbr += 1
				if self.frameNbr == self.videoTotalFrame:
					self.exitClient()
				print(f"Display frame number: {self.frameNbr}/{self.frameCurrent}")
				
			except IndexError as e:
				print(f"Packet Loss Occured at Frame {self.frameNbr}")
				self.frameLoss += 1
				sleep(self.DEFAULT_TIME_CLOCK*10/1000)
				continue
			self.currentFrameDisplayedIndex += 1
	#TODO
		
	def connectToServer(self):
		"""Connect to the Server. Start a new RTSP/TCP session."""
		self.rtspSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.rtspSocket.connect((self.serverAddr,self.serverPort))
		self.isRtspSocketCreated = True
	#TODO
	
	def sendRtspRequest(self, requestCode):
		"""Send RTSP request to the server."""	
		print(requestCode)
		self.rtspSocket.sendall(requestCode)
		self.rtspSeq += 1
		return self.recvRtspReply()
	#TODO
	
	def recvRtspReply(self):
		"""Receive RTSP reply from the server."""
		responseMessage = None
		while True:
			try:
				responseMessage= self.rtspSocket.recvfrom(65535)
				break
			except socket.timeout:
				continue
		responseMessage = responseMessage[0]
		response = self.parseRtspReply(responseMessage.decode('utf-8'))
		if self.sessionId == 0:
			self.sessionId = int((response[2].split(' '))[1])
		return response
	#TODO
		
	def parseRtspReply(self, data):
		"""Parse the RTSP reply from the server."""
		response = data.split('\n')
		response_header = response[0].split(' ')
		if response_header[1] != '200':
			raise Exception(f"Error message: {repr(response)}")
		return response
	#TODO
	
	def openRtpPort(self):
		"""Open RTP socket binded to a specified port."""
		#-------------
		# TO COMPLETE
		#-------------
		# Create a new datagram socket to receive RTP packets from the server
		self.rtpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		# Set the timeout value of the socket to 0.5sec
		# ...
		self.rtpSocket.settimeout(0.5)
		self.rtpSocket.bind((self.DEFAULT_LOCAL_HOST,self.rtpPort))
		

	def handler(self):
		"""Handler on explicitly closing the GUI window."""
		print("Close UI")
		# Potentail bugs for closing, join closed socket or joined thread
		if self.state != self.INIT:
			self.exitClient()
		
		self.rtspSocket.close()
		self.master.destroy()
		sys.exit()
	#TODO

	def getVideoRemainTime(self):
		#TODO: Show remain time into UI:
		return (self.videoTotalFrame - self.frameNbr) * self.videoDuration / self.videoTotalFrame
		
