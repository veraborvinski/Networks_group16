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
	def __init__(self, n, ul = []):
		self.name = n
		self.userList = ul

class Server:
	def __init__(self, n = "Server", h = "fc00:1337::17", p = 6667, un = 0, ul = []):
		self.name = n
		self.host = h
		self.port = p
		self.usernr = un
		self.userList = ul
   
def bind_new_socket(server, h, p):
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
			server.userList[server.usernr] = User(connection, client_address, "", "", "", "","")
			server.usernr = server.usernr+1
			break

#the main method runs as long as the server is running
def main():
	main_server = Server()
	bind_new_socket(main_server, main_server.host, main_server.port)
	#keeping server alive using infinite loop and receiving messages: https://acloudguru.com/blog/engineering/creating-an-irc-bot-with-python3
	x=True
	while x:
		#how to decode messages: https://acloudguru.com/blog/engineering/creating-an-irc-bot-with-python3
		try:
			msg = (main_server.userList[main_server.usernr-1].connection.recv(2048).decode("UTF-8")).strip('nr')
			process(msg, main_server)
		except:
			x=False
		
def process_msg(msg, server):
        #what messages to respond to for bot to login: https://www.rfc-editor.org/rfc/rfc2812#section-3.1.2
	#if the message from client includes "NICK", save their nickname and welcome them
	if msg.find("NICK") != -1:
		nickname = msg.split(" ",1)[1].strip("\n")
		server.userList[server.usernr-1].nickname = nickname
		welcome()
	#if the message from client includes "USER", save their user info
	elif msg.find("USER") != -1:
		username = msg.split(" ",4)[1]
		server.userList[server.usernr-1].username = username
		hostname = msg.split(" ",4)[2]
		server.userList[server.usernr-1].hostname = hostname
		servername = msg.split(" ",4)[3]
		server.userList[server.usernr-1].servername = servername
		realname = msg.split(" ",4)[4].strip("\n")
		server.userList[server.usernr-1].realname = realname
	#if the message from client includes "NICK", stop recieving messages and break the loop
	elif msg.find("QUIT") != -1:
		print("Not recieving messages")
		close_connection(server)
	elif msg.find("JOIN") != -1:
                join_channel(msg, server.userList[server.usernr-1].nickname)
	else:
                send_error(server)

def welcome():
        userList[usernr-1].connection.send(bytes("Welcome "+userList[usernr-1].nickname, "UTF-8"))

def close_connection(server):
        #close the current connection
	print("Closing current connection")
	server.userList[usernr-1].connection.close()

def send_error(server):
        server.userList[usernr-1].connection.send(bytes("unknown command", "UTF-8"))

def join_channel(msg, user):
	channel = Channel(msg.split(' ',1)[1])
	channel.userList.append(user)

main()
   
