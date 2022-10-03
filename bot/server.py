import sys
import socket

host = "labpc013.computing.dundee.ac.uk"
botnick = "bot"
channel = "##test"

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as irc:
    irc.bind((HOST, PORT))
    irc.listen()
    conn, addr = irc.accept()
    with conn:
        print(f"Connected by {addr}")
        while True:
            data = conn.recv(1024)
            if not data:
                break
            conn.sendall(data)
    
