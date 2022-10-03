import sys
import socket

host = "labpc013.computing.dundee.ac.uk"
botnick = "bot"
channel = "##test"

irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
irc.connect((host,6667))
irc.setblocking(False)
irc.send(bytes("USER "+ botnick +" "+ botnick +" "+ botnick + " " + botnick + "n", "UTF-8"))
irc.send("NICK "+botnick+"\n")
irc.send("JOIN "+channel+"\n")

while 1:
    test = irc.recv(2040)

input()
    
