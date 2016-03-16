#EzzyBot 2016
#Created by zz & Bowserinator & BWBellairs (freenode @ #ezzybot)

import socket
import ssl as securesl
import logging
from time import sleep
import time
import traceback
import json, thingdb
from Queue import Queue
from threading import Thread
from fnmatch import fnmatch
import socks
from base64 import b64encode
import colours
import os

class systemExit(Exception):
    pass

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
            log.send(raw)
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
            log.send(raw)
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
        #self.send("PRIVMSG #ezzybot :{} {}".format(conn, info))
        for fullcommand, command in self.commands.iteritems():
            if command["commandname"] == info["args"].lstrip():
                conn.notice(info['nick'], " {} : {}".format(fullcommand, command['help']))
                conn.msg(info['channel'], command['help'])
                
    def list(self, info=None, conn=None):
        return " ".join([self.commands[command]["commandname"] for command in self.commands.keys()])
        
    def bot_quit(self, conn, info):
        conn.quit()
    def __init__(self):
        self.commands = {}
        #---Built-in---#
        self.commands["!help"] = {"function": self.help, "help": "This command.", "prefix": "!", "commandname": "help", "perms": "all"}
        self.commands["!quit"] = {"function": self.bot_quit, "help": "Forces the bot :to quit", "prefix":"!", "commandname": "quit", "perms":["admin"]}
        self.commands["!list"] = {"function": self.list, "help":"list : lists all commands", "prefix": "!", "commandname": "list", "perms": "all"}
    
    def assign(self,function, help_text, commandname, prefix="!", perms="all"):
        self.commands[prefix+commandname] = {"function": function, "help": help_text, "prefix": prefix, "commandname": commandname, "fullcommand": prefix+commandname, "perms": perms}
    def send(self, data):
        log.send(data)
        self.irc.send("{}\r\n".format(data))
    def sendmsg(self, chan, msg):
        self.irc.send("PRIVMSG {0} :{1}\n".format(chan, msg))#.encode('utf-8'))
    def printrecv(self):
        self.ircmsg = self.recv()
        for line in self.ircmsg:
            log.receive(line)
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
    def run_plugin(self, function, plugin_wrapper, channel, info):
        try:
            self.output =function(info=info, conn=plugin_wrapper)
            if self.output != None:
                if channel.startswith("#"):
                    plugin_wrapper.msg(channel,"[{}] {}".format(info['nick'], str(self.output)))
                else:
                    plugin_wrapper.msg(info['nick'],"| "+str(self.output))
                #plugin_wrapper.msg(channel,"| "+str(self.output))
        except Exception as e:
            for line in str(e).split("\n"):
                self.log.error(line)
    def confirmsasl(self):
        while True:
            received = " ".join(self.printrecv()) 
            auth_msgs = [":SASL authentication successful", ":SASL authentication failed", ":SASL authentication aborted"]
            if auth_msgs[0] in received: 
                return True
            elif auth_msgs[1] in received or auth_msgs[2] in received:
                return False
            
    def run(self, config={}):
        global log
        self.host = config.get("host") or "irc.freenode.net"
        self.port = config.get("port") or 6667
        self.ssl = config.get("SSL") or False
        self.sasl = config.get("SASL") or False
        self.do_auth = config.get("do_auth") or False
        self.auth_pass = config.get("auth_pass") or None
        self.auth_user = config.get("auth_user") or None
        self.nick = config.get("nick") or "EzzyBot"
        self.ident = config.get("indent") or "EzzyBot"
        self.realname = config.get("realname") or "EzzyBot: a simple python framework for IRC bots."
        self.channels = config.get("channels") or ["#EzzyBot"]
        self.analytics = config.get("analytics") or True
        self.quit_message = config.get("quit_message") or "EzzyBot: a simple python framework for IRC bots."
        self.flood_protection = config.get("flood_protection") or False
        self.permissions = config.get("permissions") or {}
        self.proxy = config.get("proxy") or False
        self.proxy_type = config.get("proxy_type") or "SOCKS5"
        self.proxy_host = config.get("proxy_host") or ""
        self.proxy_port = config.get("proxy_port") or 1080
        self.proxy_type = {"SOCKS5": socks.SOCKS5, "SOCKS4": socks.SOCKS4}[self.proxy_type]
        self.log_channel = config.get("log_channel") or "#ezzybot"
        
        self.colours = colours.colours()
        self.colors = colours.colours()
        if self.proxy == True:
            self.sock = socks.socksocket()
            self.sock.set_proxy(socks.SOCKS5, self.proxy_host, self.proxy_port)
        else:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.ssl == True and self.proxy == False:
            self.irc = securesl.wrap_socket(self.sock)
        else:
            self.irc = self.sock
        log = logging.Logging(self.log_channel, connection_wrapper(self.irc, config, self.flood_protection))
        self.log = log
        #log.debug("Connecting to {} at port {}".format(self.host, self.port))
        self.irc.connect((self.host, self.port))
        self.printrecv()
        if self.sasl:
            saslstring = b64encode("{0}\x00{0}\x00{1}".format(
                            self.auth_user, self.auth_pass).encode("UTF-8"))
            saslstring = saslstring.decode("UTF-8")
            self.send("CAP REQ :sasl".encode("UTF-8"))
            self.send("AUTHENTICATE PLAIN".encode("UTF-8"))
            self.send("AUTHENTICATE {0}".format(saslstring).encode(
                    "UTF-8"))
            authed = self.confirmsasl()
            #authed = True
            if authed:
                self.send("CAP END".encode("UTF-8"))
                self.send("NICK {}".format(self.nick))
                self.send("USER {} * * :{}".format(self.ident, self.realname))
            else:
                log.error("[ERROR] SASL aborted. exiting.")
                self.send("QUIT :[ERROR] SASL aborted".encode("UTF-8"))
                raise systemExit()

        else:
            self.send("NICK {}".format(self.nick))
            self.send("USER {} * * :{}".format(self.ident, self.realname))
            if self.do_auth:
                self.irc.send("PRIVMSG nickserv :identify {0} {1}\r\n".format(
                        self.auth_user, self.auth_pass).encode("UTF-8"))
        sleep(5)
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
                        self.command = self.ircmsg.split(" :",1)[1].split(" ")[0]
                        self.args = self.message.replace(self.command, "")
                        self.info = {"nick": self.nick, "channel": self.channel, "hostname": self.hostname, "ident": self.ident, "mask": self.mask, "message": self.message, "args": self.args}
                       
                        if self.command in self.commands.keys():
                            permissions_wrapper = permissions_class(self.permissions)
                            if permissions_wrapper.check(self.commands[self.command]['perms'], self.mask) or self.commands[self.command]['perms'] == "all":
                                self.plugin_wrapper=connection_wrapper(self.irc, self.flood_protection, config)
                                plugin_thread= Thread(target=self.run_plugin, args=(self.commands[self.command]['function'], self.plugin_wrapper,self.channel,self.info,))
                                plugin_thread.setDaemon(True)
                                plugin_thread.start()
        except KeyboardInterrupt:
            self.send("QUIT :{}".format(self.quit_message)) # send automatically does log.send
            self.irc.close()
        except:
            traceback.print_exc()
