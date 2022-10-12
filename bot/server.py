#author: vera borvinski, nicole jackson
#matriculation nr: 2421818, 2415277
#importing modules
import sys
import socket
import datetime
import random
import select

#class used to hold user objects
class User:
	def __init__(self, c, a, n, u, h, s, r):
		self.connection = c
		self.address = a
		self.nickname = n
		self.username = u
		self.hostname = h
		self.servername = s
		self.realname = r

class Channel:
	def __init__(self, n, ul):
		self.name = n
		self.userList = ul

class Server:
	def __init__(self, n, h, p, un, ul):
		self.name = n
		self.host = h
		self.port = p
		self.userNumber = un
		self.userList = ul

#defining global variables
host = "fc00:1337::17"
port = 6667
usernr = 0
userList = list(range(100))
   
def bind_new_socket(h, p):
	global usernr
	#how to set up server socket: https://medium.com/python-pandemonium/python-socket-communication-e10b39225a4c
	irc = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)

	#try to bind socket to host and port
	#control for errors: https://medium.com/python-pandemonium/python-socket-communication-e10b39225a4c
	try:
		irc.bind((h, p))
	except socket.error as err:
		print(err)
		sys.exit(1)
	 
	#listen to whether a client connects   
	irc.listen(1)
	
	#while a connection is not recieved, let user know we are waiing for a connection
	while True:
		print('\nWaiting for a connection')
		connection, client_address = irc.accept()
		if connection is not None:
			userList[usernr] = User(connection, client_address, "", "", "", "","")
			usernr = usernr+1
			break

#the main method runs as long as the server is running
def main():
	bind_new_socket(host, port)
	#keeping server alive using infinite loop and receiving messages: https://acloudguru.com/blog/engineering/creating-an-irc-bot-with-python3
	while True:
		#how to decode messages: https://acloudguru.com/blog/engineering/creating-an-irc-bot-with-python3
		msg = (userList[usernr-1].connection.recv(2048).decode("UTF-8")).strip('nr')
		print(msg)
		
def process_msg(msg):
        #what messages to respond to for bot to login: https://www.rfc-editor.org/rfc/rfc2812#section-3.1.2
	#if the message from client includes "NICK", save their nickname and welcome them
	if msg.find("NICK") != -1:
		nickname = msg.split(" ",1)[1].strip("\n")
		userList[usernr-1].nickname = nickname
		welcome()
	#if the message from client includes "USER", save their user info
	elif msg.find("USER") != -1:
		username = msg.split(" ",4)[1]
		userList[usernr-1].username = username
		hostname = msg.split(" ",4)[2]
		userList[usernr-1].hostname = hostname
		servername = msg.split(" ",4)[3]
		userList[usernr-1].servername = servername
		realname = msg.split(" ",4)[4].strip("\n")
		userList[usernr-1].realname = realname
	#if the message from client includes "NICK", stop recieving messages and break the loop
	elif msg.find("QUIT") != -1:
		print("Not recieving messages")
		close_connection()
		break
	elif msg.find("JOIN") != -1:
                join_channel()
	else:
                send_error()

def welcome():
        userList[usernr-1].connection.send(bytes("Welcome "+userList[usernr-1].nickname, "UTF-8"))

def close_connection():
        #close the current connection
	print("Closing current connection")
	userList[usernr-1].connection.close()

def send_error():
        userList[usernr-1].connection.send(bytes("unknown command", "UTF-8"))

def join_channel():
        print("blabla")

main()
   
