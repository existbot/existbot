#EzzyBot 2016
#Created by zz & Bowserinator & BWBellairs & IndigoTiger (freenode @ #ezzybot)
import socks, re, json, traceback, time, socket, os, glob, importlib, requests, pkg_resources
import ssl as securesl
import logging, wrappers, limit
from time import sleep
from threading import Thread
from base64 import b64encode
from util import hook, colours, repl, web, other
#from importlib import reload
import builtin
mtimes = {}


class systemExit(Exception):
    pass

class bot(object):
    def importPlugins(self, do_reload=False):
        result =  glob.glob(os.path.join(os.getcwd(), "plugins", "*/*.py"))
        hook.commands = {}
        hook.regexs = []
        hook.triggers = []
        for i in result:
            if i in mtimes:
                if os.path.getmtime(i) != mtimes[i]:
                    plugin = reload(importlib.import_module("plugins."+i.split("/")[-2]))
                    globals()["plugins."+i.split("/")[-2]] = plugin
            mtimes[i] = os.path.getmtime(i)
    def reload_bot(self,info, conn):
        self.log.debug("Attemping Reload...", info.channel)
        self.importPlugins(True)
        self.log.debug("Plugins sucessfully imported", info.channel)
        self.__init__()
        self.commands.update(hook.commands)
        self.triggers = self.triggers+hook.triggers
        self.regex = self.regex+hook.regexs
        self.log.debug("Plugins sucessfully added to list", info.channel)

    def __init__(self):
        self.commands = builtin.commands
        self.commands["!reload"] = {"function": self.reload_bot, "help":"reload : reloads all commands", "prefix": "!", "commandname": "reload", "perms": "all", "requires": []}
        self.triggers = []
        self.regex = []
        self.plugins = []
        
    #def assign(self,function, help_text, commandname, prefix="!", perms="all"):
    #    p = plugin.Plugin(function)
    #    p.load()
    #    self.commands[prefix+commandname] = {"function": p.function, "help": help_text, "prefix": prefix, "commandname": commandname, "fullcommand": prefix+commandname, "perms": perms}
    #    self.plugins.append(p)
    
    def trigger(self, function, trigger):
        self.triggers.append({"trigger": trigger, "function": function})
    def trigger_regex(self, function, search_for):
        self.regex.append({"regex": search_for, "function": function})
    def send(self, data):
        log.send(data)
        self.irc.send("{}\r\n".format(data))
    def sendmsg(self, chan, msg):
        self.irc.send("PRIVMSG {0} :{1}\n".format(chan, msg))#.encode('utf-8'))
    
    def fifo(self):
        while True:
            got_message = raw_input("")
            self.send(got_message) # input() for py 3
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
                    plugin_wrapper.msg(channel,"[{}] {}".format(info.nick, str(self.output)))
                else:
                    plugin_wrapper.msg(info.nick,"| "+str(self.output))
                #plugin_wrapper.msg(channel,"| "+str(self.output))
        except Exception as e:
            traceback.print_exc()
            self.log.error(self.colours.VIOLET+"Caused by {}, using command '{}' in {}".format(info.mask, info.message, info.channel))
            if channel != self.config_log_channel:
                plugin_wrapper.msg(channel, self.colours.RED+"Error! See {} for more info.".format(self.config_log_channel))
            for line in str(e).split("\n"):
                self.log.error("[{0}] {1}".format(type(e).__name__, line))
    def run_trigger(self, function, plugin_wrapper, info):
        try:
            function(info=info, conn=plugin_wrapper)
        except Exception as e:
            self.log.error(self.colours.VIOLET+"Caused by {}, using command '{}' in {}".format(info.mask, info.message, info.channel))
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
            
    def run(self, config):
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
        self.config_flood_protection = config.get("flood_protection") or True
        self.config_permissions = config.get("permissions") or {}
        self.config_proxy = config.get("proxy") or False
        self.config_proxy_type = config.get("proxy_type") or "SOCKS5"
        self.config_proxy_host = config.get("proxy_host") or ""
        self.config_proxy_port = config.get("proxy_port") or 1080
        self.config_proxy_type = {"SOCKS5": socks.SOCKS5, "SOCKS4": socks.SOCKS4}[self.config_proxy_type]
        self.config_log_channel = config.get("log_channel") or "#ezzybot-debug"
        self.config_pass = config.get("pass") or None
        self.config_fifo = config.get("fifo") or True # Do you want fifo True?
        self.config_command_limiting_initial_tokens = config.get("command_limiting_initial_tokens") or 20
        self.config_command_limiting_message_cost = config.get("command_limiting_message_cost") or 4
        self.config_command_limiting_restore_rate = config.get("command_limiting_restore_rate") or 0.13
        self.config_limit_override = config.get("limit_override") or ["admin", "dev"]
        self.add_devs = config.get("add_devs") or False
        
        #load dev list
        if self.add_devs:
            devs = eval(str(requests.get("http://ezzybot.github.io/DEV.txt").text.replace("\n", "")))
            self.config_permissions['dev'] = devs
        #get latest version on pypi
        self.latest = requests.get("https://pypi.python.org/pypi/ezzybot/json").json()['info']['version']
        
        if self.config_fifo:
            self.fifo_thread = Thread(target=self.fifo)
            self.fifo_thread.setDaemon(True)
            self.fifo_thread.start()
        
        self.colours = colours.colours()
        self.colors = colours.colours() #americans
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
        result =  glob.glob(os.path.join(os.getcwd(), "plugins", "*/*.py"))
        for i in result:
            mtimes[i] = 0
        self.importPlugins()
        
        self.commands.update(hook.commands)
        self.triggers = self.triggers + hook.triggers
        self.regex = self.regex + hook.regexs
        self.log = log
        wrappers.specify(self.log)
        #log.debug("Connecting to {} at port {}".format(self.host, self.port))
        self.irc.connect((self.config_host, self.config_port))
        self.printrecv()
        if self.config_pass != None:
            self.send("PASS "+self.config_pass)
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
                self.send("NICK {}".format(self.config_nick))
                self.send("USER {} * * :{}".format(self.config_ident, self.config_realname))
            else:
                log.error("[ERROR] SASL aborted. exiting.")
                self.send("QUIT :[ERROR] SASL aborted".encode("UTF-8"))
                raise systemExit()

        else:
            self.send("NICK {}".format(self.config_nick))
            self.send("USER {} * * :{}".format(self.config_ident, self.config_realname))
            if self.config_do_auth:
                self.irc.send("PRIVMSG nickserv :identify {0} {1}\r\n".format(
                        self.config_auth_user, self.config_auth_pass).encode("UTF-8"))
        sleep(5)
        self.send("JOIN {}".format(",".join(self.config_channels)))
        
        self.repl = repl.Repl(wrappers.connection_wrapper(self.irc, config, self.config_flood_protection, self))
        self.limit = limit.Limit(self.config_command_limiting_initial_tokens, self.config_command_limiting_message_cost, self.config_command_limiting_restore_rate, self.config_limit_override, self.config_permissions)
        try:
            if str(self.latest) != str(pkg_resources.get_distribution("ezzybot").version):
                log.debug("New version of ezzybot ({}) is out, check ezzybot/ezzybot on github for installation info.".format(str(self.latest))) # dev build support?
        except:
            log.error("Checking ezzybot's version failed.")
        try:
            while True:
                self.msg = self.printrecv()
                for irc_msg in self.msg:
                    self.irc_msg = irc_msg.replace(":", "", 1)
                    self.t = irc_msg.split()
                    #:zz!Zc-zz@mixtape.zzirc.xyz PRIVMSG #ezzybot :test
                    if self.t[0] == "PING":
                        self.send("PONG {}".format(" ".join(self.t[1:])))
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
                        self.info = other.toClass(self.info)
                        info=self.info
                        if self.command in self.commands.keys():
                            permissions_wrapper = wrappers.permissions_class(self.config_permissions)
                            if permissions_wrapper.check(self.commands[self.command]['perms'], self.mask) or self.commands[self.command]['perms'] == "all":
                                if self.limit.command_limiter(info):
                                    self.plugin_wrapper=wrappers.connection_wrapper(self.irc, config, self.config_flood_protection, self, self.commands[self.command]['requires'])
                                    plugin_thread= Thread(target=self.run_plugin, args=(self.commands[self.command]['function'], self.plugin_wrapper,self.channel,self.info,))
                                    plugin_thread.setDaemon(True)
                                    plugin_thread.start()
                                else:
                                    self.plugin_wrapper=wrappers.connection_wrapper(self.irc, config, self.config_flood_protection, self, self.commands[self.command]['requires'])
                                    self.plugin_wrapper.notice(info.nick, "This command is rate limited, please try again later")
                    if self.triggers != []:
                        for trigger in self.triggers:
                            if trigger['trigger'] == "*":
                                self.info = {"raw": irc_msg, "trigger": trigger['trigger'], "split": irc_msg.split(" ")}
                                self.info = other.toClass(self.info)
                                self.plugin_wrapper=wrappers.connection_wrapper(self.irc, config, self.flood_protection, self, trigger['requires'])
                                trigger_thread= Thread(target=self.run_trigger, args=(trigger['function'], self.plugin_wrapper,self.info,))
                                trigger_thread.setDaemon(True)
                                trigger_thread.start()
                            if trigger['trigger'].upper() == "PRIVMSG" and self.t[1] == "PRIVMSG":
                                self.nick = self.irc_msg.split("!")[0]
                                self.channel = self.irc_msg.split(' PRIVMSG ')[-1].split(' :')[0]
                                self.hostname = self.irc_msg.split(" PRIVMSG ")[0].split("@")[1].replace(" ","")
                                self.ident = self.irc_msg.split(" PRIVMSG ")[0].split("@")[0].split("!")[1]
                                self.mask = self.irc_msg.split(" PRIVMSG ")[0]
                                self.message = self.irc_msg.split(" :",1)[1]
                                self.info = {"nick": self.nick, "channel": self.channel, "hostname": self.hostname, "ident": self.ident, "mask": self.mask, "message": self.message}
                                self.info = other.toClass(self.info)
                                self.plugin_wrapper=wrappers.connection_wrapper(self.irc, config, self.config_flood_protection, self, trigger['requires'])
                                trigger_thread= Thread(target=self.run_trigger, args=(trigger['function'], self.plugin_wrapper,self.info,))
                                trigger_thread.setDaemon(True)
                                trigger_thread.start()
                            elif trigger['trigger'] == self.t[1]:
                                self.info = {"raw": irc_msg, "trigger": trigger['trigger'], "split": irc_msg.split(" ")}
                                self.info = other.toClass(self.info)
                                self.plugin_wrapper=wrappers.connection_wrapper(self.irc, config, self.config_flood_protection, self, trigger['requires'])
                                trigger_thread= Thread(target=self.run_trigger, args=(trigger['function'], self.plugin_wrapper,self.info,))
                                trigger_thread.setDaemon(True)
                                trigger_thread.start()
                    if self.regex != []:
                        for search in self.regex:
                            searched = re.search(search['regex'], irc_msg)
                            if searched != None:
                                self.info = {"raw": irc_msg, "regex": search['regex'], "split": irc_msg.split(" "), "result": searched}
                                self.info = other.toClass(self.info)
                                self.plugin_wrapper=wrappers.connection_wrapper(self.irc, config, self.config_flood_protection, self, search['requires'])
                                trigger_thread= Thread(target=self.run_trigger, args=(search['function'], self.plugin_wrapper,self.info,))
                                trigger_thread.setDaemon(True)
                                trigger_thread.start()
                        
        except KeyboardInterrupt:
            self.send("QUIT :{}".format(self.config_quit_message)) # send automatically does log.send
            self.irc.close()
        except:
            traceback.print_exc()
