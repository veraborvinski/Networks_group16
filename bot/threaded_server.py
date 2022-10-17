#author: vera borvinski

#matriculation nr: 2421818

#importing modules

import sys

import socket

import datetime

import random



from _thread import *

import threading

 

print_lock = threading.Lock()



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

   

# thread function

def threaded(c):

    while True:

 

        # data received from client

       msg = connection.recv(2048).decode("UTF-8")).strip('nr')

        if not msg:

            print('Bye')

             

            # lock released on exit

            print_lock.release()

            break

 

        # reverse the given string from client

        msg = msg[::-1]

 

        # send back reversed string to client

        c.send(msg)

 

    # connection closed

    c.close()

 

 

def main():

	#how to set up server socket: https://medium.com/python-pandemonium/python-socket-communication-e10b39225a4c

    	irc = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)

    

    #try to bind socket to host and port

	#control for errors: https://medium.com/python-pandemonium/python-socket-communication-e10b39225a4c

	try:

		irc.bind((host, port))

	except socket.error as err:

		print(err)

		sys.exit(1)

 

	# put the socket into listening mode

	irc.listen(5)

	print("\nWaiting for a connection")



	# a forever loop until client wants to exit

	while True:

		# establish connection with client

		connection, client_address = irc.accept()



		# lock acquired by client

		print_lock.acquire()



		# Start a new thread and return its identifier

		start_new_thread(threaded, (connection,))

	irc.close()

    

main()
