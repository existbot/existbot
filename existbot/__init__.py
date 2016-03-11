#ExistBot 2016
#Created by zz & Bowserinator (freenode)

import socket
import ssl as securesl
from time import sleep

def send(data):
    print("[SEND] {}".format(data))
    irc.send("{}\r\n".format(data).encode("UTF-8"))

def recv():
    part = ""
    data = ""
    while not part.endswith("\r\n"):
        part = irc.recv(2048)
        part = part.decode()
        data += part
    data = data.splitlines()
    return data

def printrecv():
    ircmsg = recv()
    for line in ircmsg:
        print("[RECV] {}".format(line))
    return ircmsg

def run(host=None, port=6667, ssl=False, nick=None, ident="EzzyBot", realname="EzzyBot ", channels=["#EzzyBot"]):
    global irc
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if ssl == True:
        irc = securesl.wrap_socket(sock)
    else:
        irc = sock
    if host == None:
        raise NameError('host')
    else:
        irc.connect((host, port))
    if nick == None:
        raise NameError('nick')
    else:
        send("NICK {}".format(nick))
    send("USER {} * * :{}".format(ident, realname))
    for channel in channels:
        send("JOIN {}".format(channel))
        sleep(1)
    while True:
        printrecv()

#Testing just for now
run(port=6697, ssl=True, host="irc.freenode.net", nick="zz|test", channels=["##BWbellairs-bots"])

