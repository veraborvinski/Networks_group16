#author: vera borvinski
#matriculation nr: 2421818
#importing modules
import sys
import socket
import datetime
import random

#defining global variables
#to be made editable in cl
host = "fc00:1337::17"
port = 6667
nickname = ""
username = ""
hostname = ""
servername = ""
realname = ""
channel = "#test"
l = 1
   
#how to set up server socket: https://medium.com/python-pandemonium/python-socket-communication-e10b39225a4c
irc = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
irc.bind((host, port))
irc.listen(1)

while l == 1:
	print('\nWaiting for a connection')
	connection, client_address = irc.accept()
	if connection is not None:
		l = 0



while True:
	msg = (connection.recv(2048).decode("UTF-8")).strip('nr')
	print(msg)
	if msg.find("NICK") != -1:
		nickname = msg.split(" ",2)[1]
		print("\nWelcome "+nickname)
	elif msg.find("USER") != -1:
		username = msg.split(" ")[1]
		hostname = msg.split(" ")[1]
		servername = msg.split(" ")[1]
		realname = msg.split(" ")[1]
	else:
		print("unknown command")
		
   
