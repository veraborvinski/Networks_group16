#author: vera borvinski, nicole jackson
#matriculation nr: 2421818, 2415277
#importing modules
import sys
import socket
import datetime
import random
import selectors
import types

sel = selectors.DefaultSelector()

#defining global variables
host = "fc00:1337::17"
port = 6667
usernr = 0
userList = list(range(100))

#class used to hold user objects
class User:
	def __init__(self, n):
		self.name = n
	
class Channel:
	def __init__(self, n, ul = set()):
		self.name = n
		self.userList = ul

class Server:
	def __init__(self, n, ul = set()):
		self.name = n
		self.userList = ul
   
irc = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)

#try to bind socket to host and port
#control for errors: https://medium.com/python-pandemonium/python-socket-communication-e10b39225a4c
try:
	irc.bind((host, port))
except socket.error as err:
	print(err)
	sys.exit(1)
	 
#listen to whether a client connects   
irc.listen(1)

irc.setblocking(False)
sel.register(irc, selectors.EVENT_READ, data=None)

def accept_wrapper(sock):
	conn, addr = sock.accept()  # Should be ready to read
	print(f"Accepted connection from {addr}")
	conn.setblocking(False)
	data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
	events = selectors.EVENT_READ | selectors.EVENT_WRITE
	sel.register(conn, events, data=data)

def service_connection(key, mask):
	sock = key.fileobj
	data = key.data
	if mask & selectors.EVENT_READ:
		recv_data = sock.recv(1024)  # Should be ready to read
		if recv_data:
			data.outb += recv_data
		else:
			print(f"Closing connection to {data.addr}")
			sel.unregister(sock)
			sock.close()
	if mask & selectors.EVENT_WRITE:
		if data.outb:
			msg = (sock.recv(2048).decode("UTF-8")).strip('nr')
			process_msg(msg)
			sent = sock.send(data.outb)  # Should be ready to write
			data.outb = data.outb[sent:]

def process_msg(msg):
	print(msg)
	cmd = msg.split(" ",1)[0]
	argument = msg.split(" ",1)[1].strip("\n")
	if cmd == "NICK":
		process_nick(argument)
	elif cmd == "USER":
		process_user(argument)
	elif cmd == "JOIN":
		process_join(argument)
	else:
		print(error)

def process_nick(arg):
	server = Server("server")
	user = User(arg)
	server.userList.add(user)
	print(user.name)

def process_user(arg):
	print("hi")

def process_join(arg):
	channel = Channel(arg) 
			
print('\nWaiting for a connection')

try:
	#while a connection is not recieved, let user know we are waiing for a connection
	while True:
		events = sel.select(timeout=None)
		for key, mask in events:
			if key.data is None:
				accept_wrapper(key.fileobj)
			else: 
				service_connection(key, mask)
except KeyboardInterrupt:
	print(error)
finally:
	sel.close()
	
#the main method runs as long as the server is running
def main():
	#keeping server alive using infinite loop and receiving messages: https://acloudguru.com/blog/engineering/creating-an-irc-bot-with-python3
	while True:
		#how to decode messages: https://acloudguru.com/blog/engineering/creating-an-irc-bot-with-python3
		msg = (connection.recv(2048).decode("UTF-8")).strip('nr')
		print("hi")
		process_msg(msg)
        
main()
   
