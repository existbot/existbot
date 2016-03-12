#EzzyBot 2016
#Created by zz & Bowserinator & BWBellairs(freenode)

import socket
import ssl as securesl
from time import sleep
import traceback
import json
from Queue import Queue
from threading import Thread
    

class flood_protect_class:
    def __init__(self):
        self.irc_queue = Queue()
        self.irc_queue_running = False

    def queue_thread(self):
        while True:
            try:
                connection, raw = self.irc_queue.get_nowait()
            except:
                self.irc_queue_running = False
                break
            connection.send(raw)
            print "[QUEUE-SEND) "+raw
            sleep(0.5)

    def queue_add(self, connection, raw):
        self.irc_queue.put((connection, raw))
        if not self.irc_queue_running:
            self.irc_queue_running = True
            self.queuet = Thread(target=self.queue_thread)
            self.queuet.daemon = True
            self.queuet.start()

flood_protect = flood_protect_class()

class connection_wrapper:
    def __init__(self, connection, config, flood_protection=True):
        self.irc=connection
        self.flood_protection = flood_protection
        self.config = config
    def send(self, raw):
        if self.flood_protection==False:
            print "[SEND) {}".format(raw)
            self.irc.send("{}\r\n".format(raw))#.encode("UTF-8"))
        else:
            flood_protect.queue_add(self.irc, "{}\r\n".format(raw))#.encode("UTF-8"))
    def msg(self, channel, message):
        self.send("PRIVMSG {} :{}".format(channel, message))
    def quit(self, message=""):
        self.send("QUIT :"+message)


class bot(object):
    def __init__(self):
        self.commands = {}

    def assign(self,function, help_text, commandname, prefix="!"):
        self.commands[prefix+commandname] = {"function": function, "help": help_text, "prefix": prefix, "commandname": commandname, "fullcommand": prefix+commandname}

    def send(self, data):
        print("[SEND] {}".format(data))
        self.irc.send("{}\r\n".format(data))
    def sendmsg(self, chan, msg):
        self.irc.send("PRIVMSG {0} :{1}\n".format(chan, msg))#.encode('utf-8'))
    def printrecv(self):
        self.ircmsg = self.recv()
        for line in self.ircmsg:
            print("[RECV) {}".format(line))
        return self.ircmsg
    def recv(self):
        self.part = ""
        self.data = ""
        while not self.part.endswith("\r\n"):
            self.part = self.irc.recv(2048)
            #part = part
            self.data += self.part
        self.data = self.data.splitlines()
        return self.data
    def run(self, config={}):
        self.host = config.get("host") or "irc.freenode.net"
        self.port = config.get("port") or 6667
        self.ssl = config.get("ssl") or False
        self.nick = config.get("nick") or "EzzyBot"
        self.ident = config.get("indent") or "EzzyBot"
        self.realname = config.get("realname") or "EzzyBot: a simple python framework for IRC bots."
        self.channels = config.get("channels") or ["#EzzyBot"]
        self.analytics = config.get("analytics") or True
        self.quit_message = config.get("quit_message") or "EzzyBot: a simple python framework for IRC bots."
        self.flood_protection = config.get("flood_protection") or True
    
        if self.analytics == True:
            self.channels.append("#EzzyBot")
    
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.ssl == True:
            self.irc = securesl.wrap_socket(self.sock)
        else:
            self.irc = self.sock
        print "[SEND) Connect {}:{}".format(self.host, self.port)
        self.irc.connect((self.host, self.port))
        self.send("NICK {}".format(self.nick))
        self.send("USER {} * * :{}".format(self.ident, self.realname))
        self.send("JOIN {}".format(",".join(self.channels)))
        
        try:
            while True:
                self.msg = self.printrecv()
                for irc_msg in self.msg:
                    self.irc_msg = irc_msg.strip(":")
                    self.t = irc_msg.split()
                    #:zz!Zc-zz@mixtape.zzirc.xyz PRIVMSG #ezzybot :test
                    if self.t[0] == "PING":
                        self.send("PONG {}".format(" ".join(self.t[1:])))
                    elif self.t[1] == "PRIVMSG":
                        self.ircmsg = self.irc_msg
                        self.nick = self.ircmsg.split("!")[0]
                        self.channel = self.ircmsg.split(' PRIVMSG ')[-1].split(' :')[0]
                        self.hostname = self.ircmsg.split(" PRIVMSG ")[0].split("@")[1].replace(" ","")
                        self.ident = self.ircmsg.split(" PRIVMSG ")[0].split("@")[0].split("!")[1]
                        self.mask = self.ircmsg.split(" PRIVMSG ")[0]
                        self.message = self.ircmsg.split(" :")[1]
                        self.info = {"nick": self.nick, "channel": self.channel, "hostname": self.hostname, "ident": self.ident, "mask": self.mask, "message": self.message}
                        self.command = self.ircmsg.split(" :",1)[1].split(" ")[0]
                       
                        if self.command in self.commands.keys():
                            self.plugin_wrapper=connection_wrapper(self.irc, self.flood_protection, config)
                            self.output =self.commands[self.command]['function'](info=self.info, conn=self.plugin_wrapper)
                            if self.output != None:
                                self.plugin_wrapper.msg(self.channel,self.output)
        except KeyboardInterrupt:
            self.send("QUIT :{}".format(self.quit_message))
            self.irc.close()
        except:
            traceback.print_exc()
