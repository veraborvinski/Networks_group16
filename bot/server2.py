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

irc = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)

#defining global variables
host = "fc00:1337::17"
port = 6667

#class used to hold user objects
class User:
	def __init__(self, n, s = "server", soc = irc):
		self.name = n
	
class Channel:
	def __init__(self, n, ul = set()):
		self.name = n
		self.userList = ul

class Server:
	def __init__(self, n, ul = set()):
		self.name = n
		self.userList = ul
		
	def start(self):
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
		print('\nWaiting for a connection')

		try:
			#while a connection is not recieved, let user know we are waiing for a connection
			while True:
				events = sel.select(timeout=None)
				for key, mask in events:
					if key.data is None:
						sock = key.fileobj
						conn, addr = sock.accept()  
						# Should be ready to read
						conn.setblocking(False)
						data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
						sel.register(conn, selectors.EVENT_READ, data=data)
					else: 
						service_connection(key, mask)
		except KeyboardInterrupt:
			print("error")
		finally:
			sel.close()

def service_connection(key, mask):
	sock = key.fileobj
	data = key.data
	if mask & selectors.EVENT_READ:
		msg = (sock.recv(4096).decode("UTF-8")).strip('nr')
		if msg:
			print("hi")
			process_msg(msg)
		else:
			print(f"Closing connection to {data.addr}")
			sel.unregister(sock)
			sock.close()

def process_msg(msg):
	print(msg)
	cmd = msg.split(" ")[0]
	argument = msg.split(" ")[1].strip("\n")
	if cmd == "NICK":
		process_nick(argument)
	elif cmd == "USER":
		process_user(argument)
	elif cmd == "JOIN":
		process_join(argument)
	else:
		print("error")

def process_nick(arg):
	user = User(arg)
	print(user.name)

def process_user(arg):
	print("hi")

def process_join(arg):
	channel = Channel(arg) 
	channel.userlist.add()
	
#the main method runs as long as the server is running
def main():
	server = Server("server")
	server.start()
        
main()
   
