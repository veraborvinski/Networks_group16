#author: vera borvinski, nicole jackson
#matriculation nr: 2421818, 2415277
#importing modules
import sys
import socket
import datetime
import random
import selectors
import types
import time

sel = selectors.DefaultSelector()

irc = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)

#defining global variables
host = "fc00:1337::17"
port = 6667
user_count = 0

#class used to hold user objects
class User:
	def __init__(self, n, u, r, s = "server", sock = None, h = host):
		self.name = n
		self.server = s
		self.username = u
		self.host = h
		self.realname = r
		self.socket = sock
	
class Channel:
	def __init__(self, n, us = set()):
		self.name = n
		self.user_set = us

class Server:
	def __init__(self, n):
		self.name = n
		self.user_dict: Dict[Socket, User] = {}
	
	def add_user(self, s):
		self.user_dict[s].append(User("", "", "", sock = s))
		
	def close_connection(self):
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

		#irc.setblocking(False)
		sel.register(irc, selectors.EVENT_READ, data=None)
		print('\nWaiting for a connection')
	
		#while a connection is not recieved, let user know we are waiing for a connection
		while True:
			time.sleep(1)
			events = sel.select(timeout=None)
			for key, mask in events:
				if key.data is None and key.fileobj == irc:
					sock = key.fileobj
					conn, addr = sock.accept()  
					# Should be ready to read
					conn.setblocking(False)
					data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
					sel.register(conn, selectors.EVENT_READ, data=data)
					# create a new User object with empty name/user/realname and the socket
					self.add_user(sock)				
				else: 
					sock = key.fileobj
					# retrieve the User object from server dictionary of users using the socket
					user = user_dict[sock]
					service_connection(key, mask, user)
					print("plop out service")

def service_connection(key, mask, user):
	sock = key.fileobj
	data = key.data
	if mask & selectors.EVENT_READ:
		msg = (sock.recv(1024).decode("UTF-8"))
		if msg:
			print("hi")
			process_msg(msg, user)
		#else:
			#send_ping(data.addr)
			#if process_msg != 1:
				#server.close_connection()

def process_msg(msg):
	msgs = msg.split("\r\n")
	i = 0
	while i < len(msgs):
		print(msgs[i])
		currmsg = msgs[i].strip('nr')
		cmd = currmsg.split(" ", 1)[0]
		argument = currmsg.split(" ", 1)[1]
		if cmd == "NICK":
			process_nick(argument, user)
		elif cmd == "USER":
			process_user(argument, user)
		elif cmd == "JOIN":
			process_join(argument)
		elif cmd == "QUIT":
			process_quit()
		elif cmd == "PONG":
			return 1
		else:
			print("error")
		i = i+1

def process_nick(arg, user):
	user.name = arg
	
def process_user(arg, user):
	user_details = arg.split(" ")
	user.username = user_details[0]
	user.realname = user_details[3]
	RPL_WELCOME(user)
	RPL_YOURHOST(user)
	RPL_CREATED(user)

def process_join(arg):
	channel = Channel(arg) 
	channel.userlist.add()

def process_quit():
	server.close_connection()

def send_ping(address):
	ircsend("PING", address)
	
def RPL_WELCOME(user):
	msg = "001 Welcome to the Internet Relay Network " + user.name + "!" + user.username + "@" + user.host
	ircsend("", msg, user)
	
def RPL_YOURHOST(user):
	ircsend("","002 Your host is server, running version 1", user)
 
def RPL_CREATED():
	ircsend("","003 This server was created 21/10-22", user)
	
def ircsend(cmd, args, user):
	user.sock.send(bytes(cmd + " " + args + "\r\n", "UTF-8"))
	
#the main method runs as long as the server is running
def main():	
	server.start()
	
server = Server("server")      
main()
