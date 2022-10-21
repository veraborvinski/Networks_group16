#author: vera borvinski, nicole jackson, dimitar valkov
#matriculation nr: 2421818, 2415277, 2413179
#importing modules
import sys
import socket
import datetime
from datetime import datetime, timedelta
import random
import selectors
import types
import time

#using sockets to build a multi-connection server: https://realpython.com/python-sockets/#multi-connection-server
#creating the selector
#this will allow multiple clients to join the server
sel = selectors.DefaultSelector()

#how to connect socket to IPv6: https://stackoverflow.com/questions/5358021/establishing-an-ipv6-connection-using-sockets-in-python
#IPv6 is used because the host is an IPv6 address
irc = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)

#defining global variables
host = "fc00:1337::17"
port = 6667

#class used to hold User objects
class User:
	"""
	constructor for class User

	:param str n: initial value for name
	:param str u: initial value for username
	:param str r: initial value for realname
	:param str m: initial value for mask
	:param str s: initial value for server
	:param Socket soc: initial value for socket
	:param str h: initial value for host
	"""
	def __init__(self, n, u, r, m, s = "server", sock = None, h = host):
		self.name = n
		self.server = s
		self.username = u
		self.host = h
		self.realname = r
		self.socket = sock
		self.mask = m
		#last time user was seen active
		self.last_active = datetime.today()
		self.ping = False

#class used to hold Channel objects	
class Channel:
	"""
	constructor for class Channel

	:param str n: initial value for name
	"""
	def __init__(self, n):
		self.name = n
		#dictionary to store user objects in channel, is initialised to empty
		self.user_dict: Dict[Socket, User] = {}

#class used to hold Server objects
class Server:
	"""
	constructor for class Server

	:param str n: initial value for name
	"""
	def __init__(self, n):
		self.name = n
		#dictionary to store user objects in server, is initialised to empty
		self.user_dict: Dict[Socket, User] = {}
		#dictionary to store channel objects in server, is initialised to empty
		self.channel_dict = {}
	
	"""
	the add_user function responds to adds a user to the server's user dictionary

	:param Socket s: the user's socket
	"""
	def add_user(self, s):
		#all values are being initialised to empty strings, values will be added further on
		self.user_dict[s] = User("", "", "", "", sock = s)
		
	"""
	the close_connection function closes a user's socket and removes them from the server

	:param User user: the user whose connection is being closed
	"""	
	def close_connection(self, user):
		#remove use from multi-connection server: https://realpython.com/python-sockets/#multi-connection-server
		#unregister the selector
		sel.unregister(user.socket)
		#close the socket
		user.socket.close()
		#delete the user from the server's user dictionary
		del self.user_dict[user.socket]
	
	"""
	the start function manages a server object
	
	"""	
	def start(self):
		#try to bind socket to host and port
		#bind socket andcontrol for errors: https://medium.com/python-pandemonium/python-socket-communication-e10b39225a4c
		#try to bind the socket to the host and port
		try:
			irc.bind((host, port))
		#except socket error
		except socket.error as err:
			print(err)
			sys.exit(1)
	 
		#listen to whether a client connects   
		irc.listen(1)
		
		#how to use selectors: https://realpython.com/python-sockets/#multi-connection-server
		#register selector with event read(it can recieve data from the client)
		sel.register(irc, selectors.EVENT_READ, data=None)
		
		#let client now we are waiting for a connection
		print('\nWaiting for a connection...')
	
		#try to keep the socket alive
		try:
			#keeping server connection alive using infinite loop and receiving data: https://acloudguru.com/blog/engineering/creating-an-irc-bot-with-python3
			last_check = datetime.today()
			while True:
				#check if users have been idle
				#add seconds to time: https://bobbyhadz.com/blog/python-add-seconds-to-datetime
				#check whether users are idle, inspiration: https://github.com/jrosdahl/miniircd/blob/master/miniircd
				#only works if other users are active
				if last_check + timedelta(seconds = 10)  < datetime.today():
						if self.user_dict:
							user_list = list()
							for key, value in self.user_dict.items():
								#send ping message if user has been idle for 90s
								if value.last_active + timedelta(seconds = 90) < datetime.today() and value.last_active + timedelta(seconds = 180) > datetime.today():
									if value.ping == False:
										send_ping(value)
								#close user's connection if idle for 180s
								elif value.last_active + timedelta(seconds = 180) < datetime.today():
									user_list.append(value)
							for x in user_list:
								process_quit("", x)
							last_check = datetime.today()
				events = sel.select(timeout=None)
				for key, mask in events:
					#checking data is coming from the server socket
					if key.data is None and key.fileobj == irc:
						sock = key.fileobj
						#accept client connection from server
						conn, addr = sock.accept() 
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
		#except when interrupted by terminal
		except KeyboardInterrupt:
		    print("Caught keyboard interrupt, exiting")
		#finally, close the selector
		finally:
		    sel.close()
"""
the service_connection function takes data from a socket and processes it

:param key: key assosiated with user's connection
:param mask: mask assosiated with user's connection
:param user: the user whose connection is sending data
"""	
#taken from: #how to use selectors: https://realpython.com/python-sockets/#multi-connection-server	    
def service_connection(key, mask, user):
	sock = key.fileobj
	data = key.data
	#if data is being read
	if mask & selectors.EVENT_READ:
		#receiving and decoding messages: https://acloudguru.com/blog/engineering/creating-an-irc-bot-with-python3
		msg = (sock.recv(1024).decode("UTF-8"))
		#if there is a message, process it
		if msg:
			process_msg(msg, user)

"""
the process_msg function takes a message and splits it into an IRC command and an argument

:param key: key assosiated with user's connection
:param mask: mask assosiated with user's connection
:param user: the user whose connection is sending data
"""
def process_msg(msg, user):
	#update user#s acticity status
	user.last_active = datetime.today()
	
	#if there are several messages coming in at once, split them into a list
	msgs = msg.split("\r\n")
	
	#remove blank lines: https://stackoverflow.com/questions/4842057/easiest-way-to-ignore-blank-lines-when-reading-a-file-in-python
	msgs = (line.rstrip() for line in msgs) 
	msgs = list(line for line in msgs if line)
	
	#set count to 0
	i = 0
	#loop through all messages in msgs list
	while i < len(msgs):
		#print the message in the terminal, just to check everything#s correct
		print(msgs[i])
		#clean up message
		currmsg = msgs[i].strip('\n')
		#find irc command
		cmd = currmsg.split(" ", 1)[0]
		#try finding an argument
		try:
			argument = currmsg.split(" ", 1)[1]
		#except if there isn't one
		except: 
			argument = ""
		#all commands are found here: https://www.rfc-editor.org/rfc/rfc2812#section-3.1.7
		#all replies and errors are found here: https://www.alien.net.au/irc/irc2numerics.html
		if cmd == "NICK":
			process_nick(argument, user)
		elif cmd == "USER":
			process_user(argument, user)
		elif cmd == "JOIN":
			process_join(argument, user)
		elif cmd == "QUIT":
			process_quit(argument, user)
		#pong is just used to see if user is alive, does not need processing function
		elif cmd == "PONG":
			return 1
		elif cmd == "PRIVMSG":
			forward_msg(argument, user)
		elif cmd == "NAMES":
			process_names(argument, user)
		elif cmd == "WHO":
			process_who(argument, user)
		elif cmd == "PART":
			process_part(argument, user)
		#hex chat uses whois instead of WHOIS
		elif cmd == "WHOIS" or cmd == "whois":
			process_whois(argument, user)
		else:
			ERR_UNKNOWNCOMMAND(cmd, user)
		i = i+1
		
###ALL PROCESS COMMAND FUNCTIONS UNDER HERE!###

"""
the process_nick function gives the user a new nickname

:param str arg: the nickname
:param USer user: the user
"""
def process_nick(arg, user):
	#save the original nickname to use later
	startnick = arg
	
	#replace any invalid character: https://stackoverflow.com/questions/23996118/replace-special-characters-in-a-string-in-python
	arg = arg.translate ({ord(c): "" for c in ";;/#,.<>*~@+=()&%$£!"})
	
	#check if first character is invalid
	for i in arg:
		if i == "-" or i.isnumeric() == True:
			arg = arg[1:]
			if arg == "":
				arg = "newnick"
		else:
			break
		
	if arg == "":
		arg = "newnick"
	
	#shorten nick if longer than 9 chars
	if len(arg) > 9:
		arg = arg[:9]
	
	#if the nickname already excists, modify it
	for key, value in server.user_dict.items():
		if value.name == arg:
			arg = arg + "_"
			
	#update user's name
	user.name = arg
	
	#let hexchat know the user has a new nickname
	ircsend(":" + startnick, "NICK", arg, user)

"""
the process_user function adds more information to the user

:param str arg: the user information
:param User user: the user
"""	
def process_user(arg, user):
	#split the message into useful information
	user_details = arg.split(" ")
	
	if len(user_details) < 4:
		ERR_NEEDMOREPARAMS ("USER", user)
	
	
	#set the user's details
	user.username = user_details[0]
	user.realname = user_details[3]
	
	#create the users mask
	user.mask = user.name + "!" + user.username + "@" + user.host
	
	#welcome user to server, client is only accepted to irc server once the user and nick command have been processed
	RPL_WELCOME(user)
	RPL_YOURHOST(user)
	RPL_CREATED(user)

"""
the process_join function adds a user to a channel

:param str arg: the channel's name
:param User user: the user
"""
def process_join(arg, user):
	#if no paramater was given, call error
	if arg == "":
		ERR_NEEDMOREPARAMS("JOIN", user)
		
	#if more than one argument was given, call error
	#in our server users have to join channels one by one
	if arg.find(" ") != -1:
		ERR_TOOMANYTARGETS(arg, user)
		
	#if channel doesn't already exist, create it
	if arg not in server.channel_dict:
		channel = Channel(arg) 
		server.channel_dict[arg] = channel
	else:
		#try to find the channel in the server#s channel dictionary
		try: 
			channel = server.channel_dict[arg]
		#except when channel doesn't exist, call error
		except:
			ERR_NOSUCHCHANNEL(arg, user)
	
	#add user to channel's user dictionary
	channel.user_dict[user.socket] = user
	
	#send a message to everyone in the channel that the user has joined
	for key, value in server.channel_dict[arg].user_dict.items():
		ircsend(":" + user.mask, "JOIN", arg, value)
		
	#welcome the user
	#we couldn't find a specific numeric reply
	ircsend(":" + server.name, "PRIVMSG", arg + " :welcome", user)

"""
the process_names calls two replies

:param str arg: the channel's name, or empty for the sevrer
:param User user: the user
"""	
def process_names(arg, user):
	RPL_NAMREPLY(arg, user)
	RPL_ENDOFNAMES(arg, user)

"""
the process_who is used interchangably with the process_names function if dealing with a channel or server

:param str arg: the mask/channel, or empty for the server 
:param User user: the user
"""	
def process_who(arg, user):
	#when asked about a channel or server, give a list of users
	if arg[0] == "#" or arg == "":
		process_names(arg, user)

"""
the process_quit deletes user from all the channels it was in, displays quit message, and closes the connection

:param str arg: the quit message
:param User user: the user
"""
def process_quit(arg, user):
	#part from all the channels
	for key, value in server.channel_dict.items():
		for userkey, uservalue in value.user_dict.items():
			if uservalue.name == user.name:
				process_part(arg, user)
				
	#if there isn't a message, don't send anything
	if arg != "":
		ircsend(":" + user.mask, "QUIT", arg, user)
		
	#close the connection
	server.close_connection(user)

"""
the process_part function removes a user from a channel

:param str arg: the channel's name, and part message
:param User user: the user
"""
def process_part(arg, user):
	#seperate name from message
	channelname = arg.split(" ")[0]
	
	try:
	#try to find the channel in the server's channel dictionary
		channel = server.channel_dict[channelname]
		#try to delete the user from the channel's user dictionary
		try: 
			for key, value in channel.user_dict.items():
				ircsend(":" + user.mask, "PART", arg, value)
			del channel.user_dict[user.socket]
		
			#let everyone in the channel, including the user, know that the user has left the channel
			#send part message
			for key, value in channel.user_dict.items():
				process_names(channelname, value)
			process_names(channelname, user)
			
		#except when user is not in the channel, call error
		except:
			ERR_NOTONCHANNEL(channelname, user)
		#if the channel's user dictionary is empty, delete the channel
		if not channel.user_dict:
			del server.channel_dict[channelname]
	#except when not found, call error
	except:
		ERR_NOSUCHCHANNEL(channelname, user)

"""
the process_names calls two replies

:param str arg: the user's nickname
:param User user: the user who is asking for information
"""		
def process_whois(arg, user):
	#hex chat formats argument with nick twice
	nick = arg.split(" ")[0]
	RPL_WHOISUSER(nick, user)
	RPL_ENDOFWHOIS(nick, user)

###ALL SEND COMMAND FUNCTIONS UNDER HERE!###

"""
the send_ping function sends a ping to the user

:param User user: the user
"""
def send_ping(user):
	ircsend("", "PING", user.name, user)
	user.ping = True

"""
the forward_msg function forwards a private message from a user to another user or a channel

:param str arg: the target and the message
:param User sender: the user who sent the message
"""	
def forward_msg(arg, sender):
	foundtarget = False
	
	#try to extract the recipient for the message
	try: 
		reciever = arg.split(" :", 1)[0]
	#except if there isn't one, call error
	except:
		ERR_NORECIPIENT(sender)
		
	#if there is more than one recipient, call error
	if len(reciever.split(" ")) > 1:
		ERR_TOOMANYTARGETS(reciever, sender)
		
	#try to extract the message
	try:
		msg = arg.split(" ", 1)[1].strip("nr")
	#except if there isn't one, call error
	except:
		ERR_NOTEXTTOSEND(sender)
		
	#if the recipient is a channel
	if reciever[0] == "#":
		#try to find the channel in the server's channel dictionary
		try: 
			channel = server.channel_dict[reciever]
			foundtarget = True
		#except if it's not there, call error
		except:
			ERR_CANNOTSENDTOCHAN(reciever, sender)
			
		#send message to everyone in channel
		for key, value in channel.user_dict.items():
			if value.name != sender.name:
				ircsend(":" + sender.mask, "PRIVMSG", arg, value)
	#if the recipient is a user
	else:
		#find the recipient in server's user diectionary and send message
		for key, value in server.user_dict.items():
			if value.name == reciever:
				foundtarget = True
				ircsend(":" + sender.mask, "PRIVMSG", value.name + " :"+ msg , value)
	
	#if recipient was not found, call message
	if not foundtarget:
		ERR_NOSUCHNICK(reciever, sender)

"""
the ircsend function formats the irc message, encodes it, and sends it to socket

:param str sender: the prefix, usually a mask or a name
:param str cmd: the irc command
:param str args: the message and any other paramaters
:param User user: the user who is going to recieve the message
"""	
def ircsend(sender, cmd, args, user):
	user.socket.send(bytes(sender + " " + cmd + " " + args + "\r\n", "UTF-8"))
	
###ALL REPLY FUNCTIONS UNDER HERE!###
	
"""
the RPL_WELCOME function welcomes the user to the server

:param User user: the user
"""
def RPL_WELCOME(user):
	ircsend(user.mask, "", "001 " + "Welcome to the Internet Relay Network " + user.mask, user)

"""
the RPL_YOURHOST function informs the user about the server

:param User user: the user
"""	
def RPL_YOURHOST(user):
	ircsend(user.mask, "", "002 " + " Your host is server, running version 1", user)
 
"""
the RPL_CREATED function informs the user about when the server was created

:param User user: the user
"""
def RPL_CREATED(user):
	ircsend(user.mask, "", "003 " + "This server was created 21/10-22", user)

"""
the RPL_NAMREPLY function sends a list of names

:param str channel: the channel's name, server if blank
:param User user: the use
"""
def RPL_NAMREPLY(channel, user):
	#blank list to hold the users' nicknames
	user_list = list()
	
	#if it's a channel, add channel's users to the user list
	if channel[0] == "#":
		for key, value in server.channel_dict[channel].user_dict.items():
			user_list.append(value.name)
	#else if it's a server, add server's users to the user list
	elif channel == "":
		for key, value in server.user_dict.items():
			user_list.append(value.name)
			
	#format the message
	ircsend(":" + server.name, "", "353 " + user.name + " = " + channel + " :" + str(user_list).replace("'", "").replace("[", "").replace("]", "").replace(",", "").replace("'", ""), user)
	
"""
the RPL_ENDOFNAMES function ends the name list

:param str channel: the channel's name, server if blank
:param User user: the user
"""
def RPL_ENDOFNAMES(channel, user):
	ircsend(":" + server.name, "", "366 " + user.name + " "+ channel + " :End of /NAMES list", user)

"""	
the RPL_WHOISUSER sends a list of user information

:param str channel: the user's nickname
:param User user: the user who requested the information
"""	
def RPL_WHOISUSER(arg, user):
	for key, value in server.user_dict.items():
		if value.name == arg:
			#user name is added twice due to hexchat convention(not following irc)
			ircsend(":" + server.name, "", "311 " + value.name + " " + value.username + " " + value.username + " " + value.host + " * :" + value.realname, user)

"""
the RPL_ENDOFWHOIS function ends the whois list

:param str channel: the user's nickname
:param User user: the user who requested the information
"""
def RPL_ENDOFWHOIS(arg, user):
	ircsend(":" + server.name, "", "318 " + arg + " :End of WHOIS list" , user)
	
###ALL ERROR FUNCTIONS UNDER HERE!###
	
"""
the ERR_UNKNOWNCOMMAND tells the user the command they enetered is unknown to this server(does not mean it's not an irc command)

:param str cmd: the command
:param User user: the user
"""
def ERR_UNKNOWNCOMMAND(cmd, user):
	ircsend(":" + server.name, "", "421 " + cmd + " :Unknown command", user)
	
"""
the ERR_UNOSUCHCHANNEL tells the user the channel they enetered is unknown to this server

:param str arg: the channel
:param User user: the user
"""
def ERR_NOSUCHCHANNEL(arg, user):
	ircsend(":" + server.name, "", "403 " + arg + " :No such channel", user)

"""
the ERR_NOTONCHANNEL tells the user the channel they are not on the channel they are trying to reach

:param str arg: the channel
:param User user: the user
"""
def ERR_NOTONCHANNEL(arg, user):
	ircsend(":" + server.name, "", "442 " + arg + " :You're not on that channel", user)


"""
the ERR_NORECIPIENT tells the user the message they have tried to send has no recipient

:param User user: the user
"""
def ERR_NORECIPIENT(user):
	ircsend(":" + server.name, "", "411 " + " :No recipient", user)

"""
the ERR_TOOMANYTARGETS tells the user the message they have tried to send has too many recipients

:param str target: the recipients of the message
:param User user: the user
"""
def ERR_TOOMANYTARGETS(target, user):
	ircsend(":" + server.name, "", "407 " + target + " :Too many targets", user)

"""
the ERR_TOOMANYTARGETS tells the user the message they have tried to send has no text

:param User user: the user
"""
def ERR_NOTEXTTOSEND(user):
	ircsend(":" + server.name, "", "412 " " :No text to send", user)
	
"""
the ERR_CANNOTSENDTOCHAN tells the user the channel they have tried to send a message to cannot recieve any messages

:param str channel: the channel
:param User user: the user
"""
def ERR_CANNOTSENDTOCHAN(channel, user):
	ircsend(":" + server.name, "", "404 " + channel + " :Cannot send to channel", user)

"""
the ERR_NOSUCHNICK tells the user the nick they have tried to interact with doesn't exist

:param str nick: a nickname
:param User user: the user
"""
def ERR_NOSUCHNICK(nick, user):
	ircsend(":" + server.name, "", "401 " + nick + " :No such nick", user)
	
"""
the ERR_NEEDMOREPARAMS tells the user the number of paramaters does not match the command

:param str cmd: the command
:param User user: the user
"""
def ERR_NEEDMOREPARAMS (cmd, user):
	ircsend(":" + server.name, "", "461 " + cmd + " :Not enough parameters", user)
	
#the main method runs as long as the server is running
def main():
	#start the server	
	server.start()

#create the server	
server = Server("server")      
main()
