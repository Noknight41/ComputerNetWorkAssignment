import sys, socket, os

from ServerWorker import ServerWorker

class Server:	
	
	def main(self):
		if (os.path.isfile("port.txt")):
			os.remove("port.txt")

		try:
			SERVER_PORT = int(sys.argv[1])

		except:
			print("Usage: Server.py <Server_port>")
			print("No input found. Use default settings\n")
			SERVER_PORT = 8000

		if SERVER_PORT != 8000:
			file = open("port.txt", "w")
			file.write(str(SERVER_PORT))
			file.close()

		rtspSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		rtspSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		rtspSocket.bind(('', SERVER_PORT))
		rtspSocket.listen(5)        

		# Receive client info (address,port) through RTSP/TCP session
		while True:
			clientInfo = {}
			clientInfo['rtspSocket'] = rtspSocket.accept()
			ServerWorker(clientInfo).run()		

if __name__ == "__main__":
	(Server()).main()


