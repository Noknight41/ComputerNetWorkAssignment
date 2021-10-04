from tkinter import *
import tkinter.messagebox
import time
from PIL import Image, ImageTk
import socket, threading, sys, traceback, os
from RtpPacket import RtpPacket
from io import BytesIO

from RtpPacket import RtpPacket

CACHE_FILE_NAME = "cache-"
CACHE_FILE_EXT = ".jpg"

JPEG_EOF = b'\xff\xd9'

class Client:
	INIT = 0
	READY = 1
	PLAYING = 2
	state = INIT
	
	SETUP = 0
	PLAY = 1
	PAUSE = 2
	TEARDOWN = 3

	DEFAULT_TIME_CLOCK = 50
	
	# Initiation..
	def __init__(self, master, serveraddr, serverport, rtpport, filename):
		self.master = master
		self.master.protocol("WM_DELETE_WINDOW", self.handler)
		
		# UI and Parameter
		self.createWidgets()
		self.serverAddr = serveraddr
		self.serverPort = int(serverport)
		self.rtpPort = int(rtpport)
		self.fileName = filename
		self.rtsp_version = "RTSP/1.0"

		# Variable
		self.rtspSeq = 0 # Client Seq
		self.sessionId = 0 # Session used in SETUP and TEARDOWN
		self.requestSent = -1 # Type of Request Sent
		self.teardownAcked = 0 # Tear Down Flag
		self.frameNbr = 0 # Use for Calculating Packet Loss Rate
		self.frame_buffer = []

		self.rtpSocket = None # Socket for Client to get RTP Packet
		self.rtspSocket = None # Socket for Client to communicate with Server
		self.rtpThread = None # Thread takes care of RTP Process (listenRtp)
		self.receivingRTP = False # True = An RTP Connection is currently in active

		
		# Establish an RTSP connection
		self.connectToServer() 
		
		
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
		
		# Create a label to display the movie
		self.label = Label(self.master, height=19)
		self.label.grid(row=0, column=0, columnspan=4, sticky=W+E+N+S, padx=5, pady=5) 
	
	def connectToServer(self):
		"""Connect to the Server. Start a new RTSP/TCP session."""
		# Establish an RTSP connection
		self.rtspSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		
		# Check Socket Status 
		try:
			self.rtspSocket.connect((self.serverAddr, self.serverPort))
		except:
			tkinter.messagebox.showwarning('RTSP: Bruh')

	def setupMovie(self):
		"""Setup button handler. Starting RTP receiving thread"""
		self.openRtpPort()
		if self.state == self.INIT:
    			self.sendRtspRequest(self.SETUP) # Request Set Up
	#TODO
	
	def openRtpPort(self):
		"""Open RTP socket binded to a specified port."""
		# Create a new datagram socket to receive RTP packets from the server
		self.rtpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		
		# Set the timeout value of the socket to 0.5sec
		self.rtpSocket.settimeout(0.5)

		try:
			# Bind the socket to the address using the RTP port given by the client user
			self.rtpSocket.bind((self.serverAddr,self.rtpPort)) 
			print ("Bind RtpPort Success")

		except:
			tkinter.messagebox.showwarning('RTP: Bruh')

	def exitClient(self):
		"""Teardown button handler."""
		self.sendRtspRequest(self.TEARDOWN) # Request Tear Down
		
		# End Thread
		self.rtpThread.join()
		self.rtspSocket.close()
		self.handler()
	#TODO

	def pauseMovie(self):
		"""Pause button handler."""
		if self.state != self.PLAYING:
    			return
		self.sendRtspRequest(self.PAUSE)
		self.state = self.READY 
	#TODO
	
	def playMovie(self):
		"""Play button handler."""
		if self.state == self.PLAYING:
    			return
		if not self.receivingRTP: # prevent multiple similar thread
			self.rtpThread = threading.Thread(target=self.listenRtp)
			self.rtpThread.start()
			self.videoPlayerThread = threading.Thread(target=self.runMovie)
			self.videoPlayerThread.start()
			self.receivingRTP = True
		self.sendRtspRequest(self.PLAY)
		self.state = self.PLAYING
	#TODO

	def listenRtp(self, stop):		
		"""Listen for RTP packets."""
		while True:
			print(f"RTP Thread stop(): {stop()}")
			if stop():
				print("Client RTP Thread is safe to terminated")
				self.rtpSocket.close()
				break
			if not self.receivingRTP:
				time.sleep(self.DEFAULT_TIME_CLOCK/1000)
				continue
			try: 
				frame_payload = self.recvRTPPacket()
			except TimeoutError:
				print("RTP Socket Timeout")
				time.sleep(self.DEFAULT_TIME_CLOCK*10/1000)
				continue
			except Exception:
				print("Finish sending or RTP receive failed")
				time.sleep(self.DEFAULT_TIME_CLOCK*10/1000)
				continue
			frame = Image.open(BytesIO(frame_payload))							
			self.frameNbr += 1
			self.frame_buffer.append(frame)	
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
		if data.seqNum() == 1:
			print(data.getPayload())
		print(f"Receive frame number: {data.seqNum()}")
		return data.getPayload()

					
	def writeFrame(self, data):
		"""Write the received frame to a temp image file. Return the image file."""

		cacheimage = CACHE_FILE_NAME + str(self.sessionId) + CACHE_FILE_EXT
		try:
			file = open(cacheimage, "wb")
		except:
			print ("file open error")
		try:
			file.write(data)
		except:
			print ("file write error")
		file.close()
		return cacheimage
	#TODO

	def updateMovie(self, imageFile):
		"""Update the image file as video frame in the GUI."""
		imgTk = ImageTk.PhotoImage(imageFile)
		self.label.config(image=imgTk, width=384, height=288)
		self.label.image=imgTk
		print(self.label.image)
	#TODO
	
	def runMovie(self, stop):
		"""Update the image file as video frame in the GUI."""
		while True:
			time.sleep(self.DEFAULT_TIME_CLOCK/1000)
			print(f"Movie Thread stop(): {stop()}")
			if stop():
				print("Movie Player thread is safe to termintate")
				break
			if self.state != self.PLAYING:
				continue
			try:
				img = self.writeFrame(self.frame_buffer[self.currentFrameDisplayedIndex])
				self.updateMovie(img)
			except IndexError as e:
				print(f"Frame buffer of this index not yet downloaded")
				time.sleep(self.DEFAULT_TIME_CLOCK*10/1000)
				continue
			self.currentFrameDisplayedIndex += 1
	#TODO
		
	def sendRtspRequest(self, requestCode):
		"""Send RTSP request to the server."""	

	def encode(self, requestType):
		if requestType == self.SETUP:
			self.client_rtp_port = self.dst_port
			request_line = [
				f"SETUP {self.fileName} {self.rtsp_version}",
				f"CSeq: {self.sequence_number}",
				f"Transport: RTP/UDP; client_port= {self.client_rtp_port}"
			]
		if requestType == self.PLAY:
			request_line = [
				f"SETUP {self.fileName} {self.rtsp_version}",
				f"CSeq: {self.sequence_number}",
				f"Transport: RTP/UDP; client_port= {self.client_rtp_port}"
			]
			
		request = '\n'.join(request_line) + '\n'
		return request.encode()
	
	def recvRtspReply(self):
		"""Receive RTSP reply from the server."""
	#TODO
	
	def parseRtspReply(self, data):
		"""Parse the RTSP reply from the server."""
		response = data.split('\n')
		response_header = response[0].split(' ')
		if response_header[1] != '200':
			raise Exception(f"Error message: {repr(response)}")
		return response
		#TODO
		
	def handler(self):
		"""Handler on explicitly closing the GUI window."""
		#TODO
		print("Close UI")
		self.master.destroy()
		sys.exit()
