#EzzyBot 2016
#Created by zz & Bowserinator & BWBellairs & IndigoTiger (freenode @ #ezzybot)

import socket
import ssl as securesl
import logging
from time import sleep
import time
import traceback
import json
from threading import Thread
import socks
from base64 import b64encode
import colours
import os
import re
import wrappers

import plugin
class systemExit(Exception):
    pass

class bot(object):
    def reload(self, info, conn):
        print "RELOADING!!"
        for i in self.plugins:
            for j in self.commands: 
                if self.commands[j]["function"] == i.function:
                    i.reload()
                    self.commands[j]["function"] = i.function
        return "Reloaded"
        
        
    def help(self, conn=None, info=None):
        #self.send("PRIVMSG #ezzybot :{} {}".format(conn, info))
        for fullcommand, command in self.commands.iteritems():
            if command["commandname"] == info["args"].lstrip():
                conn.notice(info['nick'], " {0} : {1}".format(fullcommand, command['help']))
                #conn.msg(info['channel'], command['help'])
                
    def list(self, info=None, conn=None):
        return " ".join([self.commands[command]["commandname"] for command in self.commands.keys()])
        
    def bot_quit(self, conn, info):
        conn.quit()
    def __init__(self):
        self.commands = {}
        self.triggers = []
        self.regex = []
        self.plugins = []
        #---Built-in---#
        self.commands["!help"] = {"function": self.help, "help": "This command.", "prefix": "!", "commandname": "help", "perms": "all"}
        self.commands["!quit"] = {"function": self.bot_quit, "help": "Forces the bot :to quit", "prefix":"!", "commandname": "quit", "perms":["admin"]}
        self.commands["!list"] = {"function": self.list, "help":"list : lists all commands", "prefix": "!", "commandname": "list", "perms": "all"}
        self.commands["!reload"] = {"function": self.reload, "help":"reload : reloads all commands", "prefix": "!", "commandname": "reload", "perms": "all"}
    
    def assign(self,function, help_text, commandname, prefix="!", perms="all"):
        p = plugin.Plugin(function)
        p.load()
        self.commands[prefix+commandname] = {"function": p.function, "help": help_text, "prefix": prefix, "commandname": commandname, "fullcommand": prefix+commandname, "perms": perms}
        self.plugins.append(p)
    def trigger(self, function, trigger):
        p = plugin.Plugin(function)
        p.load()
        self.triggers.append({"trigger": trigger, "function": p.function})
        self.plugins.append(p)
    def trigger_regex(self, function, search_for):
        p = plugin.Plugin(function)
        p.load()
        self.regex.append({"regex": search_for, "function": p.function})
        self.plugins.append(p)
    def send(self, data):
        log.send(data)
        self.irc.send("{0}\r\n".format(data))
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
            if self.output is not None:
                if channel.startswith("#"):
                    plugin_wrapper.msg(channel,"[{0}] {1}".format(info['nick'], str(self.output)))
                else:
                    plugin_wrapper.msg(info['nick'],"| "+str(self.output))
                #plugin_wrapper.msg(channel,"| "+str(self.output))
        except Exception as e:
            traceback.print_exc()
            self.log.error(self.colours.VIOLET+"Caused by {0}, using command '{1}' in {2}".format(info['mask'], info['message'], info['channel']))
            plugin_wrapper.msg(channel, self.colours.RED+"Error! See {0} for more info.".format(self.config_log_channel))
            for line in str(e).split("\n"):
                self.log.error(line)
    def run_trigger(self, function, plugin_wrapper, info):
        try:
            function(info=info, conn=plugin_wrapper)
        except Exception as e:
            #self.log.error(self.colours.VIOLET+"Caused by {0}, using command '{1}' in {2}".format(info['mask'], info['message'], info['channel']))
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
            
    def run(self, config=None):
        if config is None:
            config = {}
        global log
        self.config_host = config.get("host") or "irc.freenode.net"
        self.config_port = config.get("port") or 6667
        self.config_ipv6 = config.get("IPv6") or False
        self.config_ssl = config.get("SSL") or False
        self.config_sasl = config.get("SASL") or False
        self.config_do_auth = config.get("do_auth") or False
        self.config_auth_pass = config.get("auth_pass") or None
        self.config_auth_user = config.get("auth_user") or None
        self.config_nick = config.get("nick") or "EzzyBot"
        self.config_ident = config.get("indent") or "EzzyBot"
        self.config_realname = config.get("realname") or "EzzyBot: a simple python framework for IRC bots."
        self.config_channels = config.get("channels") or ["#EzzyBot"]
        self.config_analytics = config.get("analytics") or True
        self.config_quit_message = config.get("quit_message") or "EzzyBot: a simple python framework for IRC bots."
        self.config_flood_protection = config.get("flood_protection") or False
        self.config_permissions = config.get("permissions") or {}
        self.config_proxy = config.get("proxy") or False
        self.config_proxy_type = config.get("proxy_type") or "SOCKS5"
        self.config_proxy_host = config.get("proxy_host") or ""
        self.config_proxy_port = config.get("proxy_port") or 1080
        self.config_proxy_type = {"SOCKS5": socks.SOCKS5, "SOCKS4": socks.SOCKS4}[self.config_proxy_type]
        self.config_log_channel = config.get("log_channel") or "#ezzybot"
        
        self.colours = colours.colours()
        self.colors = colours.colours()
        if self.config_proxy == True:
            self.sock = socks.socksocket()
            self.sock.set_proxy(socks.SOCKS5, self.config_proxy_host, self.config_proxy_port)
        elif self.config_ipv6 == True:
            self.sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        else:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.config_ssl == True and self.config_proxy == False:
            self.irc = securesl.wrap_socket(self.sock)
        else:
            self.irc = self.sock
        log = logging.Logging(self.config_log_channel, wrappers.connection_wrapper(self.irc, config, self.config_flood_protection, self))
        self.log = log
        wrappers.specify(self.log)
        #log.debug("Connecting to {} at port {}".format(self.host, self.port))
        self.irc.connect((self.config_host, self.config_port))
        self.printrecv()
        if self.config_sasl:
            saslstring = b64encode("{0}\x00{0}\x00{1}".format(
                            self.config_auth_user, self.config_auth_pass).encode("UTF-8"))
            saslstring = saslstring.decode("UTF-8")
            self.send("CAP REQ :sasl".encode("UTF-8"))
            self.send("AUTHENTICATE PLAIN".encode("UTF-8"))
            self.send("AUTHENTICATE {0}".format(saslstring).encode(
                    "UTF-8"))
            authed = self.confirmsasl()
            #authed = True
            if authed:
                self.send("CAP END".encode("UTF-8"))
                self.send("NICK {0}".format(self.config_nick))
                self.send("USER {0} * * :{1}".format(self.config_ident, self.config_realname))
            else:
                log.error("[ERROR] SASL aborted. exiting.")
                self.send("QUIT :[ERROR] SASL aborted".encode("UTF-8"))
                raise systemExit()

        else:
            self.send("NICK {0}".format(self.config_nick))
            self.send("USER {0} * * :{1}".format(self.config_ident, self.config_realname))
            if self.config_do_auth:
                self.irc.send("PRIVMSG nickserv :identify {0} {1}\r\n".format(
                        self.config_auth_user, self.config_auth_pass).encode("UTF-8"))
        sleep(5)
        self.send("JOIN {0}".format(",".join(self.config_channels)))
        try:
            while True:
                self.msg = self.printrecv()
                for irc_msg in self.msg:
                    self.irc_msg = irc_msg.replace(":", "", 1)
                    self.t = irc_msg.split()
                    #:zz!Zc-zz@mixtape.zzirc.xyz PRIVMSG #ezzybot :test
                    if self.t[0] == "PING":
                        self.send("PONG {0}".format(" ".join(self.t[1:])))
                    if self.t[1] == "PRIVMSG" and self.commands != {}:
                        self.ircmsg = self.irc_msg
                        self.nick = self.ircmsg.split("!")[0]
                        self.channel = self.ircmsg.split(' PRIVMSG ')[-1].split(' :')[0]
                        self.hostname = self.ircmsg.split(" PRIVMSG ")[0].split("@")[1].replace(" ","")
                        self.ident = self.ircmsg.split(" PRIVMSG ")[0].split("@")[0].split("!")[1]
                        self.mask = self.ircmsg.split(" PRIVMSG ")[0]
                        self.message = self.ircmsg.split(" :",1)[1]
                        self.command = self.ircmsg.split(" :",1)[1].split(" ")[0]
                        self.args = self.message.replace(self.command, "")
                        self.info = {"nick": self.nick, "channel": self.channel, "hostname": self.hostname, "ident": self.ident, "mask": self.mask, "message": self.message, "args": self.args}
                       
                        if self.command in self.commands.keys():
                            permissions_wrapper = wrappers.permissions_class(self.config_permissions)
                            if permissions_wrapper.check(self.commands[self.command]['perms'], self.mask) or self.commands[self.command]['perms'] == "all":
                                self.plugin_wrapper=wrappers.connection_wrapper(self.irc, config, self.config_flood_protection, self)
                                plugin_thread= Thread(target=self.run_plugin, args=(self.commands[self.command]['function'], self.plugin_wrapper,self.channel,self.info,))
                                plugin_thread.setDaemon(True)
                                plugin_thread.start()
                    if self.triggers != []:
                        for trigger in self.triggers:
                            if trigger['trigger'] == "*":
                                self.info = {"raw": irc_msg, "trigger": trigger['trigger'], "split": irc_msg.split(" ")}
                                self.plugin_wrapper=wrappers.connection_wrapper(self.irc, config, self.flood_protection, self)
                                trigger_thread= Thread(target=self.run_trigger, args=(trigger['function'], self.plugin_wrapper,self.info,))
                                trigger_thread.setDaemon(True)
                                trigger_thread.start()
                            if trigger['trigger'] == self.t[1]:
                                self.info = {"raw": irc_msg, "trigger": trigger['trigger'], "split": irc_msg.split(" ")}
                                self.plugin_wrapper=wrappers.connection_wrapper(self.irc, config, self.config_flood_protection, self)
                                trigger_thread= Thread(target=self.run_trigger, args=(trigger['function'], self.plugin_wrapper,self.info,))
                                trigger_thread.setDaemon(True)
                                trigger_thread.start()
                    if self.regex != []:
                        for search in self.regex:
                            searched = re.search(search['regex'], irc_msg)
                            if searched is not None:
                                self.info = {"raw": irc_msg, "regex": search['regex'], "split": irc_msg.split(" "), "result": searched}
                                self.plugin_wrapper=wrappers.connection_wrapper(self.irc, config, self.config_flood_protection, self)
                                trigger_thread= Thread(target=self.run_trigger, args=(search['function'], self.plugin_wrapper,self.info,))
                                trigger_thread.setDaemon(True)
                                trigger_thread.start()
                        
        except KeyboardInterrupt:
            self.send("QUIT :{0}".format(self.config_quit_message)) # send automatically does log.send
            self.irc.close()
        except:
            traceback.print_exc()
