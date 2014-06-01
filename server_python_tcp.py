import socket, sys, time, struct, uuid
from struct import *

#dictionary to store usernames and UUIDs
dictionary = {}

try:
	#open the socket
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	#create welcome message from welcome input
	welcomeMessage = "Welcome message: " + raw_input() + '\n'

	#checks correct amount of args are passed
	if len(sys.argv) != 2:
		sys.stderr.write("Invalid number of args. Terminating. \n")
		sys.exit()

	#sets port from args
	port = int(sys.argv[1])
	#check port is in the correct range
	if port < 1024 or port > 49151:
		sys.stderr.write("Invalid port. Terminating. \n")
		sys.exit()

	#binds the socket to the port
	try:
		s.bind(('localhost', port))
	except socket.error:
		sys.stderr.write("Could not bind port. Terminating.\n")
		sys.exit()

	#string of all messages from users
	allMessages = ""

	while 1:
		#ready to receive connections
		s.listen(1)
		#accept connection with clients
		conn, addr = s.accept()
		loop = 1
		while loop == 1:
			#receives header from client
			header = conn.recv(calcsize("!BI"))
			#unpacks header into command and length of the data
			cmd, length = struct.unpack("!BI",header)
			#receives the data
			if length != 0:
				data = conn.recv(length)
			#exit command
			if cmd == 0:
				loop = 0
				break
			#initialization command
			if cmd == 1:
				#generates uuid
				userID = str(uuid.uuid4())
				#adds username and uuid in dictionary
				dictionary[userID] = data
				#packs uuid and the welcome message to send back to client
				header = struct.pack("!BII", 2, len(userID), len(welcomeMessage))
				conn.send(header)
				conn.send(userID)
				conn.send(welcomeMessage)
			#send command
			if cmd == 4:
				if data in dictionary:
					#receives header from client
					header = conn.recv(calcsize("!BI"))
					#unpacks header into command and length of the message
					cmd, length = struct.unpack("!BI", header)
					#receives the message and adds it to the message string
					message = conn.recv(length)
					message = dictionary[data] + ":" + message + '\n\n'
					allMessages = allMessages + message
			#print command
			if cmd == 3:
				#packs header and length of the message string
				header = struct.pack("!BI", 5, len(allMessages))
				conn.send(header)
				conn.send(allMessages)
	#close the socket
	s.close()

except KeyboardInterrupt:
	if 's' in locals():
		s.close()
	sys.exit()
