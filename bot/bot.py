#author: vera borvinski
#matriculation nr: 2421818
#importing modules
import sys
import socket
import datetime
import random
import argparse

#how to deal with command line arguments: https://github.com/jrosdahl/miniircd/blob/master/miniircd
parser = argparse.ArgumentParser()
parser.add_argument('--host', nargs='?', const="fc00:1337::19", type=str, default="fc00:1337::19")
parser.add_argument('--port', nargs='?', const=6667, type=int, default=6667)
parser.add_argument('--name', nargs='?', const="bot", type=str, default="bot")
parser.add_argument('--channel', nargs='?', const="#test", type=str, default="#test")
args = parser.parse_args()
#defining global variables
host = args.host
port = args.port
name = args.name
channel = args.channel

#how to connect socket to IPv6: https://stackoverflow.com/questions/5358021/establishing-an-ipv6-connection-using-sockets-in-python
irc = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)

#connect to miniircd using IPv6
#control for errors: https://medium.com/python-pandemonium/python-socket-communication-e10b39225a4c
try:
    irc.connect((host, port))
except socket.error as err:
    print(err)
    sys.exit(1)

#the main method runs as long as the bot is running
def main():
    #how to send msg to server: https://acloudguru.com/blog/engineering/creating-an-irc-bot-with-python3
    #what messages to send to login and join channel: https://www.rfc-editor.org/rfc/rfc2812#section-3.1.2
    irc.send(bytes("NICK "+name+"\n", "UTF-8"))
    irc.send(bytes("USER "+name+" 0 * : "+name+"\n", "UTF-8"))
    irc.send(bytes("JOIN "+channel+"\n", "UTF-8"))
    #keeping server connection alive using infinite loop and receiving messages: https://acloudguru.com/blog/engineering/creating-an-irc-bot-with-python3
    while True:
        msg = (irc.recv(2048).decode("UTF-8")).strip('nr')
        print(msg)
        #given that the bot was able to connect, the user list is set to include the bot
        userList = [name]
        #identify a message in the channel and respond
        if msg.find("PRIVMSG "+channel) != -1:
            user = msg.split('!',1)[0][1:]
            respond_channel(msg, user, userList)
        #identify whether someone has left the channel and update the user list
        elif msg.find("QUIT") != -1:
            user = msg.split('!',1)[0][1:]
            if user in userList: userList.remove(user)
            print("users in this channel: ", end="")
            print(*userList, sep = ", ")
        #identify whether someone has joined the channel and update the user list
        elif msg.find("JOIN") != -1:
            irc.send(bytes("NAMES "+channel+"\n", "UTF-8"))
            msg = (irc.recv(2048).decode("UTF-8")).strip('nr')
            userList.extend(msg.split(":",3)[2].strip().split(" "))
            userList = list(set(userList))
            print("users in this channel: ", end="")
            print(*userList, sep = ", ")
        #identify a ping and reply with pong
        #this keeps the connection to the server alive
        elif msg.find("PING") != -1:
            irc.send(bytes("PONG :", "UTF-8"))
        #identify private message to the bot and respond
        elif msg.find("PRIVMSG "+name) != -1:
            user = msg.split('!',1)[0][1:]
            respond_private(user)
"""
the respond_channel function responds to a message in a channel

:param str m: the message being responded to
:param str user: the user who sent the message
:param str userList: the list of user in the channel, not a global variable because there was random errors
"""
def respond_channel(m, user, userList):
    #if the message was "!hello" the bot greets the user directly and gives the current date and time
    if "!hello" in m:
        irc.send(bytes("PRIVMSG "+ channel +" : Hello "+user+" "+str(datetime.datetime.now())+"\n", "UTF-8"))
    #if the message was !slap the bot slaps a random user in the channel with a bot
    elif "!slap" in m:
        irc.send(bytes("PRIVMSG "+ channel +" : *slaps "+str(random.choice(userList))+" with trout*\n", "UTF-8"))
"""
the respond_private function responds to a user's private message

:param str user: the user who sent the message
"""
def respond_private(user):
    #how to read random line from file: https://stackoverflow.com/questions/3540288/how-do-i-read-a-random-line-from-one-file
    #responds to user with a random fact
    irc.send(bytes("PRIVMSG "+ user +" "+random.choice(list(open('randomfacts.txt')))+"\n", "UTF-8"))

#calling the main function
main()
