from .__init__ import __version__
from .util.config import config as Config
from .limit import Limit
from . import wrappers, builtin, util, logging
from .util import hook, colours, repl, other
import pyfiglet, sys, requests, socks, socket, time, threading, os, glob, traceback, re, glob, thingdb, warnings, importlib
import ssl as _ssl
from base64 import b64encode

if (sys.version_info > (3, 0)):
    from imp import reload
if (sys.version_info > (3, 4)):
    from importlib import reload

class Socket(object):
    '''Handles receiving and sending data'''
    def __init__(self, ipv6=False, ssl=False, proxy=False, proxy_host=None, proxy_port=None, proxy_type=None):
        self.attachments = []
        
        if proxy:
            self.attachments.append("proxy")
            self.socket = socks.socksocket()
            self.socket.set_proxy(proxy_type, proxy_host, proxy_port)
        elif ipv6:
            self.attachments.append("IPv6")
            self.socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        else:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if ssl and not proxy:
            self.attachments.append("SSL")
            self.socket = _ssl.wrap_socket(self.socket)
        self.connect = self.socket.connect
        self.close = self.socket.close
        self.connected = False
    def recv(self):
        self.part = ""
        self.data = ""
        while not self.part.endswith("\r\n"):
            self.part = self.socket.recv(2048)
            self.part = self.part.decode("UTF-8", "ignore")
            self.data += self.part
        self.data = self.data.splitlines()
        return self.data
    def printrecv(self):
        self.received_message = self.recv()
        if hasattr(self, "log"):
            for line in self.received_message:
                self.log.receive(line)
        #for line in self.received_message:
        return self.received_message
    def send(self, data):
        if type(data) is not str:
            data = data.decode("UTF-8")
        self.socket.send("{0}\r\n".format(data).encode("UTF-8"))
        #print("[SEND] "+str(data))
        if hasattr(self, "log"):
            self.log.send(str(data))

class ConfigError(Exception):
    '''ConfigError Exception'''
    pass

class SASLError(Exception):
    '''SASLError Exception'''
    pass

class NickRegain(Exception):
    '''NickRegain Exception'''
    pass

class ezzybot(Socket):
    def __init__(self, config=None):
        print(pyfiglet.Figlet(font='slant').renderText('EzzyBot {}'.format(__version__)))
        print(sys.version)
        self.config = config
        self.latest = requests.get("https://pypi.python.org/pypi/ezzybot/json", verify=False).json()['info']['version']
        self.colours = colours.colours()
        self.colors = self.colours
        self.defaults()
        self.ctcp = {"VERSION": 'EzzyBot {}'.format(__version__), "TIME": time.time}
    def defaults(self):
        self.mtimes = {}
        self.events = builtin.events
        self.modules = {}
    def importmodule(self, module_name, path, do_reload=False):
        self.modules[module_name] = importlib.import_module(module_name)
        if do_reload:
            hook.events=[]
            self.modules[module_name] = reload(self.modules[module_name])
        self.mtimes[module_name] = os.path.getmtime(path)
    def run(self, config=None):
        if self.config is None and config is None:
            raise ConfigError("No config specified.")
        elif config is not None:
             self.config = config
        self.config = Config(self.config)
        self.db_loc = os.path.join("data", self.config.host, self.config.nick.lower(), "")
        self.log = logging.log(self.config)
        if not os.path.exists(self.db_loc):
            os.makedirs(os.path.dirname(self.db_loc))
        self.db = thingdb.thing(os.path.join(self.db_loc, "state.db"))
        if "users" not in self.db.keys():
            self.db['users'] = {}
        #Set some attributes for things
        self.limit = Limit(self.config.command_limiting_initial_tokens, self.config.command_limiting_message_cost, self.config.command_limiting_restore_rate, self.config.limit_override, self.config.permissions)
        
        self.pingfreq = 15
        self.timeout = self.pingfreq * 2
        
        #self.importPlugins()
        
        self._connect()
    go = run
    def _connect(self):
        Socket.__init__(self, self.config.ipv6, self.config.ssl, self.config.proxy, self.config.proxy_host, self.config.proxy_port, self.config.proxy_type)
        self.connect((self.config.host, self.config.port))
        self.connected = False
        self.s_connected = False
        self.do_regain = False
        self.ping_timer = threading.Timer(self.pingfreq, self.ping)
        self.ping_timer.daemon = True
        
        self.repl = repl.Repl({"bot": self, "irc": self.socket, "conn": wrappers.connection_wrapper(self)})
        try:
            self.loop()
        except KeyboardInterrupt:
            print("Stopping..")
        finally:
            self.socket.close()
            self.db.close()
            
    
    def ping(self):
        now = time.time()
        diff = now - self.last_ping
        if diff > self.timeout:
            self.send("QUIT :Lagging by {} seconds".format(str(diff)))
        else:
            self.send("PING :{}".format(now))
            self.ping_timer = threading.Timer(self.pingfreq, self.ping)
            self.ping_timer.daemon = True
            self.ping_timer.start()
    def do_sasl(self):
        self.send("CAP REQ :sasl")
        while True:
            for line in self.printrecv():
                line = line.split()
                if line[0] == "AUTHENTICATE":
                    if line[1] == "+":
                        saslstring = b64encode("{0}\x00{0}\x00{1}".format(
                                        self.config.auth_user,
                                        self.config.auth_pass).encode("UTF-8"))
                        self.send("AUTHENTICATE {0}".format(saslstring.decode("UTF-8")))
                elif line[1] == "CAP":
                    if line[3] == "ACK":
                        line[4] = line[4].strip(":")
                        caps = line[4:]
                        if "sasl" in caps:
                            self.send("AUTHENTICATE PLAIN")
                elif line[1] == "903":
                    self.send("CAP END")
                    return True
                elif line[1] == "904" or line[1] == "905" or line[1] == "906":
                    error = " ".join(line[2:]).strip(":")
                    self.send("QUIT :[ERROR] {0}".format(error))
                    raise SASLError(error)

    def loop(self):
        if self.config.password is not None:
            self.send("PASS {0}".format(self.config.password))
        if self.config.sasl:
            self.do_sasl()
        self.s_connected = True
        self.send("USER {0} * * :{1}".format(self.config.ident, self.config.realname))
        self.send("NICK {0}".format(self.config.nick))
        while True:
            self.received = self.printrecv()
            for received_message in self.received:
                received_message = received_message.replace(":", "", 1)
                split_message = received_message.split()
                if split_message[0] == "PING":
                    self.send("PONG {0}".format(" ".join(split_message[1:])))
                if split_message[1] == "PONG":
                    self.last_ping = time.time()
                if split_message[0] == "ERROR":
                    if "Nickname regained by services" in received_message:
                        raise NickRegain(received_message)
                    if self.ping_timer.isAlive():
                        self.ping_timer.cancel()
                    self.close()
                    self._connect()
                if not self.connected:
                    if split_message[1] == "433" or split_message[1] == "437":
                        self.do_regain = True
                        if not hasattr(self.config, "first_nick"):
                            self.config.first_nick = self.config.nick
                        if len(self.config.nick) == 16:
                            self.config.nick = self.config.nick[:-1]+"_"
                        else:
                            self.config.nick = self.config.nick+"_"
                        self.send("NICK {0}".format(self.config.nick))
                if split_message[1] == "001":
                    self.connected = True
                    self.last_ping = time.time()
                    self.ping_timer.start()
                    if self.config.do_auth or self.config.sasl and self.do_regain:
                        self.do_regain = False
                        self.send("PRIVMSG NickServ :REGAIN {0} {1}".format(self.config.first_nick, self.config.auth_pass))
                        time.sleep(3)
                        self.config.nick = self.config.first_nick
                        self.send("NICK {0}".format(self.config.first_nick))
                    if self.config.do_auth and not self.config.sasl:
                        self.send("PRIVMSG NickServ :IDENTIFY {0} {1}".format(self.config.auth_user, self.config.auth_pass))
                    for channel in self.config.channels:
                        self.send("JOIN {0}".format(channel))
                if split_message[1] == "PRIVMSG":
                    self.ircmsg = received_message
                    self.nick = self.ircmsg.split("!")[0]
                    self.channel = self.ircmsg.split(' PRIVMSG ')[-1].split(' :')[0]
                    self.hostname = self.ircmsg.split(" PRIVMSG ")[0].split("@")[1].replace(" ","")
                    self.ident = self.ircmsg.split(" PRIVMSG ")[0].split("@")[0].split("!")[1]
                    self.mask = self.ircmsg.split(" PRIVMSG ")[0]
                    self.message = self.ircmsg.split(" :",1)[1]
                    self.command = self.ircmsg.split(" :",1)[1].split(" ")[0]
                    self.args = self.message.replace(self.command, "")
                    self._info = {"nick": self.nick, "channel": self.channel, "hostname": self.hostname, "ident": self.ident, "mask": self.mask, "message": self.message, "args": self.args, "raw": self.ircmsg}
                    self.info = other.toClass(self._info)
                    info=self.info
                    if self.message.startswith("\x01"):
                        ctcp = self.message.replace("\x01", "").upper()
                        if ctcp in self.ctcp.keys():
                            if callable(self.ctcp[ctcp]):
                                result = self.ctcp[ctcp]()
                            else:
                                result = self.ctcp[ctcp]
                            self.send("NOTICE {0} :{1} {2}".format(self.nick, ctcp, result))
                    for function in [func for func in self.events if func._event == "command"]:
                        if (function._prefix+function._commandname).lower() == self.command:
                            func = function
                            permissions_wrapper = wrappers.permissions_class(self.config.permissions)
                            if permissions_wrapper.check(func._perms, self.mask) or func._perms == "all":
                                if self.limit.command_limiter(info):
                                    self.plugin_wrapper=wrappers.connection_wrapper(self)
                                    if func._thread:
                                        plugin_thread= threading.Thread(target=self.run_plugin, args=(func, self.plugin_wrapper,self.channel,self.info,))
                                        plugin_thread.daemon = True
                                        plugin_thread.start()
                                    else:
                                        self.run_plugin(func, self.plugin_wrapper,self.channel,self.info)
                                else:
                                    self.plugin_wrapper=wrappers.connection_wrapper(self)
                                    self.plugin_wrapper.notice(info.nick, "This command is rate limited, please try again later")
                    for regex in [reg for reg in self.events if reg._event == "regex"]:
                        result = re.findall(regex._regex, received_message)
                        if result:
                            self._info['regex'] = result
                            self.info = other.toClass(self._info)
                            self.run_trigger(regex, wrappers.connection_wrapper(self), self.info)
                    if self.nick not in self.db['users'].keys():
                        self.db['users'][info.nick] = {}
                    self.db['users'][info.nick]['last_seen'] = time.time()
                    self.db['users'][info.nick]['last_msg'] = self.ircmsg
                    self.db['users'][info.nick]['mask'] = self.mask
                    if "channels" not in self.db['users'][info.nick].keys():
                        self.db['users'][info.nick]['channels']=[]
                    if info.channel not in self.db['users'][info.nick]['channels']:
                        self.db['users'][info.nick]['channels'].append(info.channel)
                for trigger in [func for func in self.events if func._event == "trigger"]:
                    if trigger._trigger == "*" or trigger._trigger.upper() == split_message[1].upper():
                        self.run_trigger(trigger, wrappers.connection_wrapper(self), other.toClass({"raw": received_message}))
                
                #TODO FIX
                for module in glob.glob(os.path.join(os.getcwd(), "plugins", "*.py")):
                    import_name = "plugins."+module.split(os.path.sep)[-1].strip(".py")
                    if import_name in self.mtimes.keys():
                        if os.path.getmtime(module) != self.mtimes[import_name]:
                            #for event in self.events:
                            #    if event.__module__ == import_name:
                            #        print("Deleting a old event from {0}".format(module))
                            #        del self.events[self.events.index(event)]
                            
                            hook.events=[]
                            self.importmodule(import_name, module, True)
                            
                            #add module attribute
                            for event in hook.events:
                                self.log.debug("New {0} found: {1}".format(event._event, event.__name__))
                                hook.events[hook.events.index(event)].__module__ = import_name

                                #for evn in self.events: 
                                for evn in [e for e in self.events if e.__module__ == import_name]:
                                    #Delete duplicates
                                    if hook.events[hook.events.index(event)].__name__ == evn.__name__:
                                        self.log.debug("Deleting a old {0}: {1}".format(evn._event, evn.__name__))
                                        del self.events[self.events.index(evn)]
                                    #Delete renamed events
                                    if evn.__module__ == import_name and evn.__name__ not in [e.__name__ for e in hook.events]:
                                        self.log.debug("Deleting a old {0}: {1}".format(evn._event, evn.__name__))
                                        del self.events[self.events.index(evn)]
                            
                            self.log.debug("Reloaded plugin " + str(module))
                            self.events = hook.events + self.events
                    else:
                        hook.events = []
                        self.importmodule(import_name, module)
                        #add module attribute
                        for event in hook.events:
                            self.log.debug("New {0} found: {1}".format(event._event, event.__name__))
                            hook.events[hook.events.index(event)].__module__ = import_name
                        self.log.debug("New plugin "+str(module))
                        self.events = hook.events+self.events
                        
                        
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
            plugin_wrapper.msg(self.config.log_channel, self.colours.VIOLET+"Caused by {0}, using command '{1}' in {2}".format(info.mask, info.message, info.channel))
            if channel != self.config.log_channel:
                plugin_wrapper.msg(channel, self.colours.RED+"Error! See {0} for more info.".format(self.config.log_channel))
            for line in str(e).split("\n"):
                plugin_wrapper.msg(self.config.log_channel, "[{0}] {1}".format(type(e).__name__, line))

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
            plugin_wrapper.msg(self.config.log_channel, self.colours.VIOLET+"Caused by {0}".format(info.raw))
            for line in str(e).split("\n"):
                plugin_wrapper.msg(self.config.log_channel, line)
    def __repr__(self):
        return "{0}(Server={1}, {2})".format(self.__class__.__name__, self.config.host, ", ".join([x+"=True" for x in self.attachments]))
def bot(config=None):
    return ezzybot(config)
