#author: vera borvinski
#matriculation nr: 2421818
import sys
import socket
import datetime
import random

#to be made editable in cl
host = "fc00:1337::19"
port = 6667
name = "bot"
channel = "#test"
userList = []

#how to connect socket to IPv6: https://stackoverflow.com/questions/5358021/establishing-an-ipv6-connection-using-sockets-in-python
irc = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
#connect to miniircd using IPv6
irc.connect((host, port))
#set blocking was causing issues but might be needed later
#irc.setblocking(False)

def main():
    #how to send msg to server: https://acloudguru.com/blog/engineering/creating-an-irc-bot-with-python3
    #What messages to send to login and join channel: https://www.rfc-editor.org/rfc/rfc2812#section-3.1.2
    irc.send(bytes("NICK "+name+"\n", "UTF-8"))
    irc.send(bytes("USER "+name+" 0 * : "+name+"\n", "UTF-8"))
    irc.send(bytes("JOIN "+channel+"\n", "UTF-8"))
    #keeping server alive using infinite loop and receiving messages: https://acloudguru.com/blog/engineering/creating-an-irc-bot-with-python3
    while 1:
        msg = (irc.recv(2048).decode("UTF-8")).strip('nr')
        print(msg)
        if msg.find("PRIVMSG") != -1:
            user = msg.split('!',1)[0][1:]
            #message = msg.split('PRIVMSG',1)[1].split(':',1)[1]
            respondChannel(msg, user)
        elif msg.find("QUIT") != -1:
            user = msg.split('!',1)[0][1:]
            print(user)
            userList.remove(user)
            print("users in this channel: ", end="")
            print(*userList, sep = ", ")
        elif msg.find("JOIN") != -1:
            irc.send(bytes("NAMES "+channel+"\n", "UTF-8"))
            msg = (irc.recv(2048).decode("UTF-8")).strip('nr')
            userList.extend(msg.split(":",3)[2].split(" "))
            print("users in this channel: ", end="")
            print(*userList, sep = ", ")
        elif msg.find("PING") != -1:
            irc.send(bytes("PONG :", "UTF-8"))
            
def respondChannel(m, user):
    if "!hello" in m:
        irc.send(bytes("PRIVMSG "+ channel +" : Hello "+user+" "+str(datetime.datetime.now())+"\n", "UTF-8"))
    elif "!slap" in m:
        print("hello")
        irc.send(bytes("PRIVMSG "+ channel +" : *slaps "+str(random.choice(userList))+" with trout*\n", "UTF-8"))

#def respondPrivate(user): 
    #irc.send(bytes("PRIVMSG "+ user +" : the earth is flat\n", "UTF-8"))

main()
