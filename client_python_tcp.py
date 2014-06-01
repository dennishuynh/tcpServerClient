import socket, time, string, sys, struct
from struct import *

#checks number of arguments
if len(sys.argv) != 4:
		sys.stderr.write("Invalid number of args. Terminating. \n")
		sys.exit()

#opens socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
hostname = sys.argv[1]
port = int(sys.argv[2])
username = sys.argv[3]

#checks port is in correct range
if port < 1024 or port > 49151:
	sys.stderr.write("Invalid port. Terminating. \n")
	sys.exit()

#connect to the server
errors = s.connect_ex((hostname, port))
if errors != 0:
	sys.stderr.write("Could not connect to server. Terminating.\n")
	sys.exit()

#packs command and username
header = struct.pack("!BI",1, len(username))
s.send(header)
s.send(username)

#receives and unpacks header into command, uuid length and welcome message length
header = s.recv(calcsize("!BII"))
cmd, uLen, wLen = struct.unpack("!BII", header)
#if not correct command type throw error
if cmd != 2:
	sys.stderr.write("Invalid server initialization. Terminating\n")
	sys.exit()
#receives uuid and welcome message
uuid = s.recv(uLen)
data = s.recv(wLen)
#checks welcome message
if "Welcome message:" not in data:
	sys.stderr.write("Invalid server initialization. Terminating\n")
	sys.exit()
print(data)

while 1:
	try:
		#receive input for type of command
		command = raw_input('Enter a command: (send, print, or exit)\n')
		if "send" == command:
			message = raw_input('Enter your message:\n')
			#packs header with send command and length of uuid
			header = struct.pack("!BI", 4, len(uuid))
			s.send(header)
			s.send(uuid)
			#packs header with send command and length of message
			header = struct.pack("!BI", 4, len(message))
			s.send(header)
			s.send(message)
		if "print" == command:
			#packs print command
			header = struct.pack("!BI", 3, 0)
			s.send(header)
			#receives header with length of message
			header = s.recv(calcsize("!BI"))
			cmd, length = struct.unpack("!BI", header)
			#checks correct command type is received
			if cmd != 5:
				sys.stderr.write("Invalid packet from server. Terminating\n")
				sys.exit()
			#receives and prints out message
			if length != 0:
				data = s.recv(length)
				print(data)
		if "exit" == command:
			#packs header to tell server that client is exiting
			header = struct.pack("!BI", 0, 0)
			s.send(header)
			break
	#allows for smooth exit with ctrl-C
	except KeyboardInterrupt:
		if 's' in locals():
			header = struct.pack("!BI", 0, 0)
			s.send(header)
			s.close()
		sys.exit()
	
	#catch socket error
	except socket.error:
		if 's' in locals():
			sys.stderr.write("Could not connect to server. Terminating.\n")
			s.close()
		sys.exit()

#close socket
s.close()
