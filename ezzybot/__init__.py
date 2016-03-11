#EzzyBot 2016
#Created by zz & Bowserinator (freenode)

import socket
import ssl as securesl
from time import sleep
import traceback

def send(data):
    print("[SEND) {}".format(data))
    irc.send("{}\r\n".format(data).encode("UTF-8"))

def recv():
    part = ""
    data = ""
    while not part.endswith("\r\n"):
        part = irc.recv(2048)
        part = part.encode('utf8')
        data += part
    data = data.splitlines()
    return data

def printrecv():
    ircmsg = recv()
    for line in ircmsg:
        print("[RECV) {}".format(line))
    return ircmsg
    
commands = {}
    
def assign(function, help_text, commandname, prefix="!"):
    commands[prefix+commandname] = {"function": function, "help": help_text, "prefix": prefix, "commandname": commandname, "fullcommand": prefix+commandname}

def sendmsg(chan, msg):
    irc.send("PRIVMSG {0} :{1}\n".format(chan, msg))#.encode('utf-8'))
    

def run(config={}):
    global irc
    host = config.get("host") or "irc.freenode.net"
    port = config.get("port") or 6667
    ssl = config.get("ssl") or False
    nick = config.get("nick") or "EzzyBot"
    ident = config.get("indent") or "EzzyBot"
    realname = config.get("realname") or "EzzyBot: a simple python framework for IRC bots."
    channels = config.get("channels") or ["#EzzyBot"]
    analytics = config.get("analytics") or True
    quit_message = config.get("quit_message") or "EzzyBot: a simple python framework for IRC bots."

    if analytics == True:
        channels.append("#EzzyBot")
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if ssl == True:
        irc = securesl.wrap_socket(sock)
    else:
        irc = sock
    print "[SEND) Connect {}:{}".format(host, port)
    irc.connect((host, port))
    send("NICK {}".format(nick))
    send("USER {} * * :{}".format(ident, realname))
    send("JOIN {}".format(",".join(channels)))
    try:
        while True:
            msg = printrecv()
            for irc_msg in msg:
                irc_msg = irc_msg.strip(":")
                t = irc_msg.split()
                #:zz!Zc-zz@mixtape.zzirc.xyz PRIVMSG #ezzybot :test
                if t[0] == "PING":
                    send("PONG {}".format(" ".join(t[1:])))
                elif t[1] == "PRIVMSG":
                    ircmsg = irc_msg
                    nick = ircmsg.split("!")[0][1:]
                    channel = ircmsg.split(' PRIVMSG ')[-1].split(' :')[0]
                    hostmask = ircmsg.split(" PRIVMSG ")[0].split("@")[1].replace(" ","")
                    
                    command = ircmsg.split(" :",1)[1]
                    if command in commands.keys():
                        output =commands[command]['function']()
                        if output != None:
                            sendmsg(channel,output)
                    
                # if len(t) >= 4:
                #     command = t[3].replace(":", "", 1)
                #     if command in commands.keys():
                #         print commands[command]['function']()
    except KeyboardInterrupt:
        send("QUIT :{}".format(quit_message))
        irc.close()
    except:
        traceback.print_exc()
