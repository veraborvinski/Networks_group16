import sys
import socket

#make all editable in cl
host = "fc00:1337::19"
port = 6667
name = "bot"
channel = "#test"

#how to connect socket to IPv6: https://stackoverflow.com/questions/5358021/establishing-an-ipv6-connection-using-sockets-in-python
irc = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
irc.connect((host, port))
irc.setblocking(False)

#how to send msg to server: https://acloudguru.com/blog/engineering/creating-an-irc-bot-with-python3
#what messages to send to login and join channel: https://www.rfc-editor.org/rfc/rfc2812#section-3.1.2
irc.send(bytes("NICK "+name+"\n", "UTF-8"))
irc.send(bytes("USER "+name+" 0 * : "+name+"\n", "UTF-8"))
irc.send(bytes("JOIN "+channel+"\n", "UTF-8"))
