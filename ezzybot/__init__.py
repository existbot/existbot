#EzzyBot 2016
#Created by zz & Bowserinator & BWBellairs(freenode)

import socket
import ssl as securesl
from time import sleep
import time
import traceback
import json, thingdb
from Queue import Queue
from threading import Thread
from fnmatch import fnmatch


class flood_protect_class(object):
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

class permissions_class(object):
    def __init__(self, permissions):
        self.permissions = permissions # {"admin": "zz!*@*"}
    def check(self, perms, mask): # perms = # ["admin"]
        if perms == "all":
            return True
        for required_perm in perms:
            for perm_mask in self.permissions[required_perm]:
                if fnmatch(mask, perm_mask):
                    return True
        return False

class thing_database(object):
    def open(self, filename="ezzybot.thing"):
        return thingdb.start(filename)
    def save(self, database, filename="ezzybot.thing"):
        return thingdb.save(database, filename)
        

class connection_wrapper(object):
    def __init__(self, connection, config, flood_protection=True):
        self.irc=connection
        self.flood_protection = flood_protection
        self.config = config
        self.db = thing_database()
    def send(self, raw):
        if self.flood_protection==False:
            print "[SEND) {}".format(raw)
            self.irc.send("{}\r\n".format(raw))#.encode("UTF-8"))
        else:
            flood_protect.queue_add(self.irc, "{}\r\n".format(raw))#.encode("UTF-8"))
    def msg(self, channel, message):
        self.send("PRIVMSG {} :{}".format(channel, message))
    def notice(self, user, message):
        self.send("NOTICE {} :{}".format(user, message))
    def quit(self, message=""):
        self.send("QUIT :"+message)


class bot(object):
    def help(self, conn=None, info=None):
        for fullcommand, command in self.commands.iteritems():
            conn.notice(info['nick'], " {} : {}".format(fullcommand, command['help']))
    def __init__(self):
        self.commands = {}
        self.commands["!help"] = {"function": self.help, "help": "This command.", "prefix": "!", "commandname": "help", "perms": "all"}
    def assign(self,function, help_text, commandname, prefix="!", perms="all"):
        self.commands[prefix+commandname] = {"function": function, "help": help_text, "prefix": prefix, "commandname": commandname, "fullcommand": prefix+commandname, "perms": perms}
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
    def run_plugin(self, function, plugin_wrapper, channel):
        try:
            self.output =function(info=self.info, conn=plugin_wrapper)
            if self.output != None:
                plugin_wrapper.msg(channel,self.output)
        except:
            traceback.print_exc()
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
        self.permissions = config.get("permissions") or {}
    
        if self.analytics == True:
            self.channels.append("#EzzyBot")
    
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.ssl == True:
            self.irc = securesl.wrap_socket(self.sock)
        else:
            self.irc = self.sock
        print "[SEND] Connect {}:{}".format(self.host, self.port)
        self.irc.connect((self.host, self.port))
        self.send("NICK {}".format(self.nick))
        self.send("USER {} * * :{}".format(self.ident, self.realname))
        self.send("JOIN {}".format(",".join(self.channels)))
        threads = {}
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
                        self.command = self.ircmsg.split(" :",1)[1].split(" ")[0]
                        self.args = self.message.replace(self.command, "")
                        self.info = {"nick": self.nick, "channel": self.channel, "hostname": self.hostname, "ident": self.ident, "mask": self.mask, "message": self.message, "args": self.args}
                       
                        if self.command in self.commands.keys():
                            permissions_wrapper = permissions_class(self.permissions)
                            if permissions_wrapper.check(self.commands[self.command]['perms'], self.mask) or self.commands[self.command]['perms'] == "all":
                                self.plugin_wrapper=connection_wrapper(self.irc, self.flood_protection, config)
                                plugin_thread= Thread(target=self.run_plugin, args=(self.commands[self.command]['function'], self.plugin_wrapper,self.channel,))
                                plugin_thread.setDaemon(True)
                                plugin_thread.start()
                            #try:
                            #    #self.output =self.commands[self.command]['function'](info=self.info, conn=self.plugin_wrapper)
                            #    #if self.output != None:
                            #    #    self.plugin_wrapper.msg(self.channel,self.output)
                            #except:
                            #    traceback.print_exc()
        except KeyboardInterrupt:
            self.send("QUIT :{}".format(self.quit_message))
            self.irc.close()
        except:
            traceback.print_exc()
