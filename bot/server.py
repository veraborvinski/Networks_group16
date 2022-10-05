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
name = "bot"
channel = "#test"
   
#how to set up server socket: https://medium.com/python-pandemonium/python-socket-communication-e10b39225a4c
irc = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
irc.bind((host, port))
irc.listen(1)

while True:
    print('\nwaiting for a connection')
    connection, client_address = irc.accept()
    try:
        data = connection.recv(unpacker.size)
        print('received {!r}'.format(binascii.hexlify(data)))

        unpacked_data = unpacker.unpack(data)
        print('unpacked:', unpacked_data)

    finally:
        connection.close()
