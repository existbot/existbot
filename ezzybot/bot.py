#EzzyBot 2016
#Created by zz & BWBellairs & IndigoTiger (freenode @ #ezzybot)
import socks, re, traceback, time, socket, os, glob, importlib, requests, pkg_resources, json, sys
import ssl as securesl
from . import logging, wrappers, limit, builtin, util
from time import sleep, time
from threading import Thread, Timer
from base64 import b64encode
from .util import hook, colours, repl, other
from pyfiglet import Figlet
from .__init__ import __version__
#from importlib import reload

class systemExit(Exception):
    pass

class bot(object):
    """ezzybot.bot()

    Creates an EzzyBot instance.
    """
    def __init__(self):
        """Initalizes bot() object
        """
        print(Figlet(font='slant').renderText('EzzyBot {}'.format(__version__)))
        print(sys.version)
        self.defaults()
        
    def defaults(self):
        """Sets defaults for ezzybot events"""
        self.do_loop = True
        self.mtimes = {}
        self.events = builtin.events
        if self.reload_bot not in self.events:
            self.events.append(self.reload_bot)
            
    def importPlugins(self):
        """importPlugins

        Imports plugins from plugins/ folder
        """
        result =  glob.glob(os.path.join(os.getcwd(), "plugins", "*/*.py"))
        hook.events = []
        for i in result:
            if i in self.mtimes:
                if os.path.getmtime(i) != self.mtimes[i]:
                    plugin = importlib.import_module("plugins."+i.split("/")[-2])
                    globals()["plugins."+i.split("/")[-2]] = plugin
            self.mtimes[i] = os.path.getmtime(i)


    def connect(self):
        if self.config_proxy:
            self.sock = socks.socksocket()
            self.sock.set_proxy(socks.SOCKS5, self.config_proxy_host, self.config_proxy_port)
        elif self.config_ipv6:
            self.sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        else:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.config_ssl and not self.config_proxy:
            self.irc = securesl.wrap_socket(self.sock)
        else:
            self.irc = self.sock
        #log.debug("Connecting to {} at port {}".format(self.host, self.port))
        self.irc.connect((self.config_host, self.config_port))
        self.repl = repl.Repl({"conn": wrappers.connection_wrapper(self), "bot": self, "irc": self.irc, "util": util})
        self.limit = limit.Limit(self.config_command_limiting_initial_tokens, self.config_command_limiting_message_cost, self.config_command_limiting_restore_rate, self.config_limit_override, self.config_permissions)
        log = logging.Logging(self.config_log_channel, wrappers.connection_wrapper(self))
        self.log = log
        wrappers.specify(log)
        if self.config_pass is not None:
            self.send("PASS "+self.config_pass)
        if self.config_sasl:
            saslstring = b64encode("{0}\x00{0}\x00{1}".format(
                            self.config_auth_user, self.config_auth_pass).encode("UTF-8"))
            saslstring = saslstring.decode("UTF-8")
            self.send("CAP REQ :sasl")
            self.send("AUTHENTICATE PLAIN")
            self.send("AUTHENTICATE {0}".format(saslstring))
            authed = self.confirmsasl()
            if authed:
                self.send("CAP END")
                self.send("NICK {0}".format(self.config_nick))
                self.send("USER {0} * * :{1}".format(self.config_ident, self.config_realname))
            else:
                self.log.error("[ERROR] SASL aborted. exiting.")
                self.send("QUIT :[ERROR] SASL aborted")
                raise systemExit()

        else:
            self.send("NICK {0}".format(self.config_nick))
            self.send("USER {0} * * :{1}".format(self.config_ident, self.config_realname))
        try:
            if str(self.latest) != str(pkg_resources.get_distribution("ezzybot").version):
                self.log.debug("New version of ezzybot ({0}) is out, check ezzybot/ezzybot on github for installation info.".format(str(self.latest)), "no_send") # dev build support?
        except:
            self.log.error("Checking ezzybot's version failed.")
        try:
            self.do_loop = True
            self.loop()
        except KeyboardInterrupt:
            self.send("QUIT :{0}".format(self.config_quit_message)) # send automatically does log.send
            self.irc.close()
            raise SystemExit()
        except:
            traceback.print_exc()
            
    def confirmsasl(self):
        """confirmsasl()

        Waits until SASL has succeeded or not.

        Returns:
            bool -- Whether SASL has succeeded or not.
        """
        while True:
            received = " ".join(self.printrecv())
            auth_msgs = [":SASL authentication successful", ":SASL authentication failed", ":SASL authentication aborted"]
            if auth_msgs[0] in received:
                return True
            elif auth_msgs[1] in received or auth_msgs[2] in received:
                return False
    
    
    def fifo(self):
        while True:
            if sys.version_info >= (3,0):
                got_message = input("")
            else:
                got_message = raw_input("")
            self.send(got_message) # input() for py 3
            
    def send(self, data):
        """send("PRIVMSG #ezzybot :Hi")

        Sends data out to the working connection and log.

        Arguments:
            data {String} -- [description]
        """
        self.log.send(data)
        self.irc.send("{0}\r\n".format(data).encode("UTF-8"))

    def sendmsg(self, chan, msg):
        """sendmsg("#ezzybot", "Hi!")

        Sends a PRIVMSG to the working connection.

        Arguments:
            chan {String} -- IRC Channel
            msg {String} -- Message to be sent
        """
        self.send("PRIVMSG {0} :{1}".format(chan, msg))

    def ping(self):
        now = time()
        diff = now - self.last_ping
        if diff > self.timeout:
            self.log.error("I am currently lagging by {} seconds, quitting in 5 seconds..".format(diff))
            sleep(5)
            self.restart("Lagging by {} seconds".format(str(diff)))
        else:
            self.send("PING :{}".format(now))
            self.ping_timer = Timer(self.pingfreq, self.ping)
            self.ping_timer.daemon = True
            self.ping_timer.start()

    def printrecv(self):
        """printrecv()

        Receives data from working connection and prints it.
        """
        self.ircmsg = self.recv()
        for line in self.ircmsg:
            self.log.receive(line)
        return self.ircmsg

    def recv(self):
        """recv()

        Receives data from working connection and returns it.
        """
        self.part = ""
        self.data = ""
        while not self.part.endswith("\r\n"):
            self.part = self.irc.recv(2048)
            self.part = self.part.decode("UTF-8")
            #part = part
            self.data += self.part
        self.data = self.data.splitlines()
        return self.data


    def run_plugin(self, function, plugin_wrapper, channel, info):
        """run_plugin(hello, plugin_wrapper, channel, info)

        Runs function and prints result/error to irc.

        Arguments:
            function {Function} -- Plugin function
            plugin_wrapper {Object} -- ezzybot.wrappers.connection_wrapper object
            channel {String} -- Channel to send result to
            info {Object} -- ezzybot.util.other.toClass object
        """
        try:
            self.output =function(info=info, conn=plugin_wrapper)
            if self.output != None:
                if channel.startswith("#"):
                    plugin_wrapper.msg(channel,"[{0}] {1}".format(info.nick, str(self.output)))
                else:
                    plugin_wrapper.msg(info.nick,"| "+str(self.output))
        except Exception as e:
            traceback.print_exc()
            self.log.error(self.colours.VIOLET+"Caused by {0}, using command '{1}' in {2}".format(info.mask, info.message, info.channel))
            if channel != self.config_log_channel:
                plugin_wrapper.msg(channel, self.colours.RED+"Error! See {0} for more info.".format(self.config_log_channel))
            for line in str(e).split("\n"):
                self.log.error("[{0}] {1}".format(type(e).__name__, line))

    def run_trigger(self, function, plugin_wrapper, info):
        """run_trigger(hello, plugin_wrapper, info)

        Runs trigger and messages errors.

        Arguments:
            function {Function} -- Plugin function
            plugin_wrapper {Object} -- ezzybot.wrappers.connection_wrapper object
            info {Object} -- ezzybot.util.other.toClass object
        """
        try:
            function(info=info, conn=plugin_wrapper)
        except Exception as e:
            self.log.error(self.colours.VIOLET+"Caused by {0}".format(info.raw))
            for line in str(e).split("\n"):
                self.log.error(line)
                
        
    def reload_bot(self,info, conn):
        self.log.debug("Attemping Reload...", info.channel)
        result =  glob.glob(os.path.join(os.getcwd(), "plugins", "*/*.py"))
        plugins = {}
        for i in result:
            if i in self.mtimes:
                if os.path.getmtime(i) != self.mtimes[i]:
                    plugin = importlib.import_module("plugins."+i.split("/")[-2])
                    plugins["plugins."+i.split("/")[-2]] = plugin
        self.defaults()
        #hook.events = []
        for pluginname, plugin in plugins.items():
            globals()[pluginname] = reload(plugin)
        self.log.debug("Plugins sucessfully imported", info.channel)
        self.events = self.events+hook.events
        #self.log.debug(str(self.events), info.channel)
        #self.log.debug(str(hook.events), info.channel)
        self.log.debug("Plugins sucessfully added to list", info.channel)
    reload_bot._commandname = "reload"
    reload_bot._prefix = "!"
    reload_bot._help = reload_bot.__doc__
    reload_bot._perms = ["admin"]
    reload_bot._event = "command"
    reload_bot._thread = False

        
    def restart(self, quit_msg="Quit"):
        self.send("QUIT :{0}".format(quit_msg))
        self.do_loop = False
        self.irc.close()

    def run(self, config):
        """run({'nick': 'EzzyBot'})

        Runs Ezzybot

        Arguments:
            config {Dict} -- The config
        """
        global log
        self.config = config
        self.config_host = config.get("host", "irc.freenode.net")
        self.config_port = config.get("port", 6667)
        self.config_ipv6 = config.get("IPv6", False)
        self.config_ssl = config.get("SSL", False)
        self.config_sasl = config.get("SASL", False)
        self.config_do_auth = config.get("do_auth", False)
        self.config_auth_pass = config.get("auth_pass", None)
        self.config_auth_user = config.get("auth_user", None)
        self.config_nick = config.get("nick", "EzzyBot")
        self.config_ident = config.get("ident", "EzzyBot")
        self.config_realname = config.get("realname", "EzzyBot: a simple python framework for IRC bots.")
        self.config_channels = config.get("channels", ["#EzzyBot"])
        self.config_analytics = config.get("analytics", True)
        self.config_quit_message = config.get("quit_message", "EzzyBot: a simple python framework for IRC bots.")
        self.config_flood_protection = config.get("flood_protection", True)
        self.config_permissions = config.get("permissions", {})
        self.config_proxy = config.get("proxy", False)
        self.config_proxy_type = config.get("proxy_type", "SOCKS5")
        self.config_proxy_host = config.get("proxy_host", "")
        self.config_proxy_port = config.get("proxy_port", 1080)
        self.config_proxy_type = {"SOCKS5": socks.SOCKS5, "SOCKS4": socks.SOCKS4}[self.config_proxy_type]
        self.config_log_channel = config.get("log_channel", "#ezzybot-debug")
        self.config_pass = config.get("pass", None)
        self.config_fifo = config.get("fifo", True)
        self.config_command_limiting_initial_tokens = config.get("command_limiting_initial_tokens", 20)
        self.config_command_limiting_message_cost = config.get("command_limiting_message_cost", 4)
        self.config_command_limiting_restore_rate = config.get("command_limiting_restore_rate", 0.13)
        self.config_limit_override = config.get("limit_override", ["admin", "dev"])
        self.add_devs = config.get("add_devs", False)
        #Lag detection
        self.last_ping = time()
        self.pingfreq = 60
        self.timeout = self.pingfreq * 2
        self.ping_timer = Timer(self.pingfreq, self.ping)
        self.ping_timer.daemon = True

        self.shared_dict = {}

        #Load dev list
        if self.add_devs:
            devs = json.loads(str(requests.get("http://ezzybot.github.io/DEV.txt", verify=False).text.replace("\n", "")))
            self.config_permissions['dev'] = devs
        #Get latest version on PyPI
        self.latest = requests.get("https://pypi.python.org/pypi/ezzybot/json", verify=False).json()['info']['version']
        #Start fifo
        if self.config_fifo:
            self.fifo_thread = Thread(target=self.fifo)
            self.fifo_thread.setDaemon(True)
        #Create some classes
        self.colours = colours.colours()
        self.colors = self.colours
        #Set mtimes to 0
        result =  glob.glob(os.path.join(os.getcwd(), "plugins", "*/*.py"))
        for i in result:
            self.mtimes[i] = 0
        self.importPlugins()
        self.defaults()
        self.connect()
        
        
    def loop(self):
        while self.do_loop == True:
            self.msg = self.printrecv()
            for irc_msg in self.msg:
                self.irc_msg = irc_msg.replace(":", "", 1)
                self.t = irc_msg.split()
                #:zz!Zc-zz@mixtape.zzirc.xyz PRIVMSG #ezzybot :test
                if self.t[0] == "PING":
                    self.send("PONG {0}".format(" ".join(self.t[1:])))
                if self.t[1] == "PONG":
                    self.last_ping = time()
                if self.t[1] == "001":
                    self.ping_timer.start()
                    self.fifo_thread.start()
                    if self.config_do_auth and not self.config_sasl:
                        self.sendmsg("NickServ", "IDENTIFY {0} {1}".format(self.config_auth_user, self.config_auth_pass))
                    sleep(5)
                    for channel in self.config_channels:
                        self.send("JOIN {0}".format(channel))
                    
                if self.t[1] == "PRIVMSG":
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
                    for function in [func for func in self.events if func._event == "command"]:
                        if (function._prefix+function._commandname).lower() == self.command:
                            func = function
                            permissions_wrapper = wrappers.permissions_class(self.config_permissions)
                            if permissions_wrapper.check(func._perms, self.mask) or func._perms == "all":
                                if self.limit.command_limiter(info):
                                    self.plugin_wrapper=wrappers.connection_wrapper(self)
                                    if func._thread:
                                        plugin_thread= Thread(target=self.run_plugin, args=(func, self.plugin_wrapper,self.channel,self.info,))
                                        plugin_thread.setDaemon(True)
                                        plugin_thread.start()
                                    else:
                                        self.run_plugin(func, self.plugin_wrapper,self.channel,self.info)
                                else:
                                    self.plugin_wrapper=wrappers.connection_wrapper(self)
                                    self.plugin_wrapper.notice(info.nick, "This command is rate limited, please try again later")
                if self.t[1] in [func._trigger for func in self.events if func._event == "trigger"] or "*" in [func._trigger for func in self.events if func._event == "trigger"]:
                    for trigger in [func for func in self.events if func._event == "trigger"]:
                        if trigger._trigger == "*":
                            self.info = {"raw": irc_msg, "trigger": trigger._trigger, "split": irc_msg.split(" ")}
                            self.info = other.toClass(self.info)
                            self.plugin_wrapper=wrappers.connection_wrapper(self)
                            if trigger._thread:
                                trigger_thread= Thread(target=self.run_trigger, args=(trigger, self.plugin_wrapper,self.info,))
                                trigger_thread.setDaemon(True)
                                trigger_thread.start()
                            else:
                                self.run_trigger(trigger, self.plugin_wrapper,self.info)
                        if trigger._trigger.upper() == "PRIVMSG" and self.t[1] == "PRIVMSG":
                            self.nick = self.irc_msg.split("!")[0]
                            self.channel = self.irc_msg.split(' PRIVMSG ')[-1].split(' :')[0]
                            self.hostname = self.irc_msg.split(" PRIVMSG ")[0].split("@")[1].replace(" ","")
                            self.ident = self.irc_msg.split(" PRIVMSG ")[0].split("@")[0].split("!")[1]
                            self.mask = self.irc_msg.split(" PRIVMSG ")[0]
                            self.message = self.irc_msg.split(" :",1)[1]
                            self.info = {"nick": self.nick, "channel": self.channel, "hostname": self.hostname, "ident": self.ident, "mask": self.mask, "message": self.message, "raw": irc_msg}
                            self.info = other.toClass(self.info)
                            self.plugin_wrapper=wrappers.connection_wrapper(self)
                            if trigger._thread:
                                trigger_thread= Thread(target=self.run_trigger, args=(trigger, self.plugin_wrapper,self.info,))
                                trigger_thread.setDaemon(True)
                                trigger_thread.start()
                            else:
                                self.run_trigger(trigger, self.plugin_wrapper,self.info)
                        elif trigger._trigger == self.t[1]:
                            self.info = {"raw": irc_msg, "trigger": trigger._trigger, "split": irc_msg.split(" ")}
                            self.info = other.toClass(self.info)
                            self.plugin_wrapper=wrappers.connection_wrapper(self)
                            if trigger._thread:
                                trigger_thread= Thread(target=self.run_trigger, args=(trigger, self.plugin_wrapper,self.info,))
                                trigger_thread.setDaemon(True)
                                trigger_thread.start()
                            else:
                                self.run_trigger(trigger, self.plugin_wrapper,self.info)
                if [func for func in self.events if func._event == "regex"] != []:
                    for func in [func for func in self.events if func._event == "regex"]:
                        searched = re.search(func._regex, irc_msg)
                        if searched is not None:
                            self.info = {"raw": irc_msg, "regex": func._regex, "split": irc_msg.split(" "), "result": searched}
                            self.info = other.toClass(self.info)
                            self.plugin_wrapper=wrappers.connection_wrapper(self)
                            if func._thread:
                                trigger_thread= Thread(target=self.run_trigger, args=(func, self.plugin_wrapper,self.info,))
                                trigger_thread.setDaemon(True)
                                trigger_thread.start()
                            else:
                                self.run_trigger(func, self.plugin_wrapper,self.info)
        self.ping_timer = Timer(self.pingfreq, self.ping)
        self.ping_timer.daemon = True
        self.connect()
