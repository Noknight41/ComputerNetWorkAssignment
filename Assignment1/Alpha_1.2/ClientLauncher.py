import sys
import os
from tkinter import Tk
from Client import Client

if __name__ == "__main__":
	try:
	 	serverAddr = sys.argv[1]
	 	serverPort = sys.argv[2]
	 	rtpPort = sys.argv[3]
	 	fileName = sys.argv[4]	
	except:
		print("Usage: ClientLauncher.py <Server_name> <Server_port> <RTP_port> <Video_file>")
		print("Invalid input. Use default settings\n")
		serverAddr = 'localhost'
		if (os.path.isfile("port.txt")):
			file = open("port.txt", "r")
			serverPort = int(file.readlines()[0])
			file.close()
			os.remove("port.txt")
		else:
			serverPort = 8000
		
		rtpPort = 25000
		fileName = 'movie.Mjpeg'	
	
	root = Tk()
	# Create a new client
	app = Client(root, serverAddr, serverPort, rtpPort, fileName)
	app.master.title("RTPClient")	
	root.mainloop()
	