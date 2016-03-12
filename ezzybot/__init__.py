#EzzyBot 2016
#Created by zz & Bowserinator (freenode)

import socket
import ssl as securesl
from time import sleep
import traceback
import json
from Queue import Queue
from threading import Thread

def send(data):
    print("[SEND) {}".format(data))
    irc.send("{}\r\n".format(data).encode("UTF-8"))

def recv():
    part = ""
    data = ""
    while not part.endswith("\r\n"):
        part = irc.recv(2048)
        part = part.decode('utf8', 'ignore')
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
    
irc_queue = Queue()
irc_queue_running = False

def queue_thread():
    global irc_queue, irc_queue_running
    while True:
        try:
            connection, raw = irc_queue.get_nowait()
        except:
            irc_queue_running = False
            break
        connection.send(raw)
        print "[QUEUE-SEND) "+raw
        sleep(0.5)

def queue_add(connection, raw):
    global irc_queue, irc_queue_running
    irc_queue.put((connection, raw))
    if not irc_queue_running:
        irc_queue_running = True
        queuet = Thread(target=queue_thread)
        queuet.daemon = True
        queuet.start()
        
    
    
class connection_wrapper:
    def __init__(self, connection, flood_protection=True):
        self.irc=connection
        self.flood_protection = flood_protection
    def send(self, raw):
        if self.flood_protection==False:
            print "[SEND) {}".format(raw)
            self.irc.send("{}\r\n".format(raw).encode("UTF-8"))
        else:
            queue_add(self.irc, "{}\r\n".format(raw).encode("UTF-8"))
        
    def msg(self, channel, message):
        self.send("PRIVMSG {} :{}".format(channel, message))
    def quit(self, message=""):
        self.send("QUIT :"+message)
        

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
    flood_protection = config.get("flood_protection") or True

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
                    nick = ircmsg.split("!")[0]
                    channel = ircmsg.split(' PRIVMSG ')[-1].split(' :')[0]
                    hostname = ircmsg.split(" PRIVMSG ")[0].split("@")[1].replace(" ","")
                    ident = ircmsg.split(" PRIVMSG ")[0].split("@")[0].split("!")[1]
                    mask = ircmsg.split(" PRIVMSG ")[0]
                    message = ircmsg.split(" :")[1]
                    info = {"nick": nick, "channel": channel, "hostname": hostname, "ident": ident, "mask": mask, "message": message}
                    command = ircmsg.split(" :",1)[1].split(" ")[0]
                    print command
                    print commands.keys()
                    if command in commands.keys():
                        plugin_wrapper=connection_wrapper(irc, flood_protection)
                        output =commands[command]['function'](info=info, conn=plugin_wrapper)
                        if output != None:
                            plugin_wrapper.msg(channel,output)
    except KeyboardInterrupt:
        send("QUIT :{}".format(quit_message))
        irc.close()
    except:
        traceback.print_exc()

#Testing area
#def hello(info=None, conn=None):
#    conn.msg("#ezzybot", "Test!")
#    return "test"
    
#assign(function=hello, help_text="Returns 'Hello!'", commandname="hello")
#run({"channels":[], "port": 6697, "ssl": True,"quit_message":"'I pretend I can touch BWBellairs[Bot] and the BWBellairs[Bot] would say something to me... '"})
