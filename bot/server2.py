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
	def __init__(self, n, us = set()):
		self.name = n
		self.user_set = us

class Server:
	def __init__(self, n, us = set()):
		self.name = n
		self.user_set = us
	
	def add_user(self, nick):
		og_len = len(user_set)
		user_set.add(User(nick))
		if oglen != len(user_set):
			return -1
		
	def close_connection():
		sel.unregister(sock)
            	sock.close()
		
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
			send_ping(data.addr)
			if process_msg != 1:
				server.close_connection()

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
	elif cmd == "QUIT":
		process_quit()
	elif cmd == "PONG"
		return 1
	else:
		print("error")

def process_nick(arg):
	while server.add_user(arg) == -1:
		arg = arg + "_"

def process_user(arg):
	arg.split(" ", 3)
	RPL_WELCOME()
	RPL_YOURHOST()
	RPL_CREATED()

def process_join(arg):
	channel = Channel(arg) 
	channel.userlist.add()

def process_quit():
	server.close_connection()
	
def ircsend(cmd, args):
    irc.send(bytes(cmd + " " + args + "\r\n", "UTF-8"))

def send_ping(address)
	ircsend("PING", address)
	
def RPL_WELCOME():
              ircsend("","001 Welcome to the Internet Relay Network <nick>!<user>@<host>")
	
def RPL_YOURHOST():
              ircsend("","002 Your host is server, running version 1")
 
def RPL_CREATED():
              ircsend("","003 This server was created 21/10-22")
	
#the main method runs as long as the server is running
def main():	
	server.start()
	
server = Server("server")      
main()
   
