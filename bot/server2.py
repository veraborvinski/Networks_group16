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
	def __init__(self, n, u, r, m, s = "server", sock = None, h = host):
		self.name = n
		self.server = s
		self.username = u
		self.host = h
		self.realname = r
		self.socket = sock
		self.mask = m
	
class Channel:
	def __init__(self, n):
		self.name = n
		self.user_dict: Dict[Socket, User] = {}

class Server:
	def __init__(self, n):
		self.name = n
		self.user_dict: Dict[Socket, User] = {}
		self.channel_dict = {}
	
	def add_user(self, s):
		self.user_dict[s] = User("", "", "", "", sock = s)
		
	def close_connection(self, user):
		sel.unregister(user.socket)
		user.socket.close()
		
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
					self.add_user(conn)									
				else: 
					sock = key.fileobj
					# retrieve the User object from server dictionary of users using the socket
					user = self.user_dict[sock]
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
		else:
			send_ping(data.addr)
			if process_msg != 1:
				server.close_connection(user)

def process_msg(msg, user):
	msgs = msg.split("\r\n")
	#remove blank lines: https://stackoverflow.com/questions/4842057/easiest-way-to-ignore-blank-lines-when-reading-a-file-in-python
	msgs = (line.rstrip() for line in msgs) # All lines including the blank ones
	msgs = list(line for line in msgs if line)
	i = 0
	while i < len(msgs):
		print(msgs[i])
		currmsg = msgs[i].strip('\n')
		cmd = currmsg.split(" ", 1)[0]
		try:
			argument = currmsg.split(" ", 1)[1]
		except: 
			argument = ""
		if cmd == "NICK":
			process_nick(argument, user)
		elif cmd == "USER":
			process_user(argument, user)
		elif cmd == "JOIN":
			process_join(argument, user)
		elif cmd == "QUIT":
			process_quit(user)
		elif cmd == "PONG":
			return 1
		elif cmd == "PRIVMSG":
			forward_msg(argument, user)
		elif cmd == "NAMES":
			process_names(argument, user)
		elif cmd == "WHO":
			process_who(argument, user);
		else:
			print("error")
		i = i+1

def process_nick(arg, user):
	startnick = arg
	for key, value in server.user_dict.items():
		if value.name == arg:
			arg = arg + "_"
	user.name = arg
	user.socket.send(bytes(":" + startnick + " NICK " + arg + "\r\n", "UTF-8"))
	print(user.name)
	
def process_user(arg, user):
	user_details = arg.split(" ")
	user.username = user_details[0]
	user.realname = user_details[3]
	user.mask = user.name + "!" + user.username + "@" + user.host
	RPL_WELCOME(user)
	RPL_YOURHOST(user)
	RPL_CREATED(user)

def process_join(arg, user):
	if arg not in server.channel_dict:
		channel = Channel(arg) 
		server.channel_dict[arg] = channel
	else:
		channel = server.channel_dict[arg]
	channel.user_dict[user.socket] = user
	for key, value in server.channel_dict[arg].user_dict.items():
		value.socket.send(bytes(":" + value.name + " JOIN " + arg + "\r\n", "UTF-8"))
	ircsend("PRIVMSG " + arg, "welcome", user)
	
def process_names(arg, user):
	RPL_NAMREPLY(arg, user)
	RPL_ENDOFNAMES(arg, user)
	
def process_who(arg, user):
	if arg[0] == "#" or arg == "":
		process_names(arg, user)

def process_quit(user):
	server.close_connection(user)

def send_ping(address):
	ircsend("PING", address)
	
def RPL_WELCOME(user):
	msg = "001 Welcome to the Internet Relay Network " + user.mask
	ircsend("", msg, user)
	
def RPL_YOURHOST(user):
	ircsend("","002 Your host is server, running version 1", user)
 
def RPL_CREATED(user):
	ircsend("","003 This server was created 21/10-22", user)

def RPL_NAMREPLY(channel, user):
	user_list = list()
	if channel != "":
		for key, value in server.channel_dict[channel].user_dict.items():
			user_list.append(value.name)
	else:
		for key, value in server.user_dict.items():
			user_list.append(value.name)
	user.socket.send(bytes(":" + server.name + " 353 " + user.name + " = " + channel + " :@" + str(user_list) + "\r\n", "UTF-8"))
	
def RPL_ENDOFNAMES(channel, user):
	user.socket.send(bytes(":" + server.name + " 366 " + user.name + " "+ channel + " :End of /NAMES list" + "\r\n", "UTF-8"))
	
def forward_msg(arg, sender):
	reciever = arg.split(" ", 1)[0]
	msg = arg.split(" ", 1)[1].strip("nr")
	#figure out how to get recievers socket
	if reciever[0] == "#":
		channel = server.channel_dict[receiver]
		for key, value in channel.user_dict.items():
			ircsend("PRIVMSG", arg, value)
	else:
		for key, value in server.user_dict.items():
			if value.username == reciever:
				ircsend("PRIVMSG", arg, value)
	
def ircsend(cmd, args, user):
	user.socket.send(bytes(user.mask + " " + cmd + " " + args + "\r\n", "UTF-8"))
	
#the main method runs as long as the server is running
def main():	
	server.start()
	
server = Server("server")      
main()
