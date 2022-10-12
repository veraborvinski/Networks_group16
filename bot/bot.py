#author: vera borvinski
#matriculation nr: 2421818
#importing modules
import sys
import socket
import datetime
import random
import argparse

#channel class stores the name and user list of a channel
class Channel:
    def __init__(self, n, ul = []):
        self.name = n
        self.userList = ul
    def add_user(self, nick):
        self.userList.append(nick)
        self.userList = list(set(self.userList))
    def add_users(self, nick):
        self.userList.extend(nick)
        self.userList = list(set(self.userList))
    def del_user(self, nick):
        if nick in self.userList: self.userList.remove(nick)
    def get_name(self):
        return self.name
    def get_userList(self):
        return self.userList

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
channel = Channel(args.channel)


#how to connect socket to IPv6: https://stackoverflow.com/questions/5358021/establishing-an-ipv6-connection-using-sockets-in-python
irc = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)

#connect to miniircd using IPv6
#control for errors: https://medium.com/python-pandemonium/python-socket-communication-e10b39225a4c
try:
    irc.connect((host, port))
except socket.error as err:
    print(err)
    sys.exit(1)

"""
the ircsend function formats and sends a message to the server

:param str cmd: command to be executed
:param str args: the arguments the command takes
"""
def ircsend(cmd, args):
    irc.send(bytes(cmd + " " + args + "\r\n", "UTF-8"))

"""
the send_join sends a join message to the server

:param str channel: channel to be joined
"""
def send_join(channel):
    ircsend("JOIN", channel)

"""
the send_privmsg function sends a private message to the server

:param str target: person/channel to recieve message
:param str msg: message to be sent
"""
def send_privmsg(target, msg):
    ircsend("PRIVMSG", target + " :" + msg)

"""
the send_nick sends nick to the server

:param str name: name for the bot
"""
def send_nick(name):
    ircsend("NICK", name)

"""
the send_user sends user to the server

:param str name: name for the bot
"""
def send_user(name):
    ircsend("USER", name+" 0 * : "+name)

"""
the ask_for_names function sends a request for names to the server

:return list: the list of names sent by the server
"""
def send_names(channel):
    ircsend("NAMES", channel)
    msg = (irc.recv(2048).decode("UTF-8")).strip('nr')
    return msg.split(":",3)[2].strip().split(" ")

"""
the pong function sends a pong to the server
"""
def send_pong():
    ircsend(bytes("PONG", ""))

#the main method runs as long as the bot is running
def main():
    #how to send msg to server: https://acloudguru.com/blog/engineering/creating-an-irc-bot-with-python3
    #what messages to send to login and join channel: https://www.rfc-editor.org/rfc/rfc2812#section-3.1.2
    send_nick(name)
    send_user(name)
    send_join(channel.get_name())
    #keeping server connection alive using infinite loop and receiving messages: https://acloudguru.com/blog/engineering/creating-an-irc-bot-with-python3
    while True:
        msg = (irc.recv(2048).decode("UTF-8")).strip('nr')
        print(msg)
        #given that the bot was able to connect, the user list is set to include the bot
        channel.add_user(name)
        process_msg(msg)

"""
the process_msg function takes a message and identifies the appropriate response for it

:param str msg: the message being responded to
"""
def process_msg(msg):
        #identify a message in the channel and respond
       #paramaters for private message: PRIVMSG command, target, text
        if msg.find("PRIVMSG "+channel.get_name()+" :!hello") != -1:
            user = msg.split('!',1)[0][1:]
            respond_hello(channel.get_name(), user)
        elif msg.find("PRIVMSG "+channel.get_name()+" :!slap") != -1:
            respond_slap(channel.get_name())
        #identify whether someone has left the channel and update the user list
        #paramaters for private message: QUIT command, quit message
        elif msg.find(" QUIT :") != -1:
            user = msg.split('!',1)[0][1:]
            channel.del_user(user)
            print("users in this channel: ", end="")
            print(*channel.get_userList(), sep = ", ")
        #identify whether someone has joined the channel and update the user list
        #paramaters for private message: JOIN command, channel
        elif msg.find(" JOIN "+channel.get_name()) != -1:           
            channel.add_users(send_names(channel.get_name()))
            print("users in this channel: ", end="")
            print(*channel.get_userList(), sep = ", ")
        #identify a ping and reply with pong
        #this keeps the connection to the server alive
        #paramaters for private message: PING command, server
        elif msg.find("PING :") != -1:
            send_pong()
        #identify private message to the bot and respond
        #paramaters for private message: PRIVMSG command, target, text
        elif msg.find("PRIVMSG "+name+" :") != -1:
            user = msg.split('!',1)[0][1:]
            respond_user(user)

"""
the respond_hello function responds to a !hello message in a channel

:param str targte: the channel being responded to
:param str user: the user who sent the message
"""
def respond_hello(target, user):
    #if the message was "!hello" the bot greets the user directly and gives the current date and time
    send_privmsg(target, "Hello "+user+" "+str(datetime.datetime.now()))

"""
the respond_slap function responds to a !hello message in a channel

:param str targte: the channel being responded to
:param str user: the user who sent the message
"""  
def respond_slap(target):
    #if the message was !slap the bot slaps a random user in the channel with a bot
    send_privmsg(target, "*slaps "+str(random.choice(channel.get_userList()))+" with trout*")

"""
the respond_user function responds to a user's private message

:param str user: the user who sent the message
"""
def respond_user(user):
    #how to read random line from file: https://stackoverflow.com/questions/3540288/how-do-i-read-a-random-line-from-one-file
    #responds to user with a random fact
    send_privmsg(user, random.choice(list(open('randomfacts.txt'))))

#calling the main function
main()
