import thingdb
from fnmatch import fnmatch
from threading import Thread
from time import sleep
from util import other
import sys
import importlib
log=None


def specify(local_log):
    """wrappers.specify(self.log)
    
    Specifys the log for wrappers to use.
    
    Arguments:
        local_log {Object} -- Log Object
    """
    global log
    log = local_log
class permissions_class(object):
    def __init__(self, permissions):
        self.permissions = permissions # {"admin": "zz!*@*"}
    def check(self, perms, mask): # perms = # ["admin"]
        if perms == "all":
            return True
        for required_perm in perms:
            if required_perm in self.permissions:
                for perm_mask in self.permissions[required_perm]:
                    if fnmatch(mask, perm_mask):
                        return True
        return False
class flood_protect_class(object):
    def __init__(self):
        self.irc_queue = []
        self.irc_queue_running = False

    def queue_thread(self):
        while True:
            try:
                connection = self.irc_queue[0][0]
                raw = self.irc_queue[0][1]
                self.irc_queue.pop(0)
            except:
                self.irc_queue_running = False
                break
            connection.send(raw)
            log.send(raw)
            sleep(1)

    def queue_add(self, connection, raw):
        self.irc_queue.append([connection, raw])
        if not self.irc_queue_running:
            self.irc_queue_running = True
            self.queuet = Thread(target=self.queue_thread)
            self.queuet.daemon = True
            self.queuet.start()
            
    def queue_add_first(self, connection, raw):
        self.irc_queue=[[connection,raw]]+self.irc_queue
        if not self.irc_queue_running:
            self.irc_queue_running = True
            self.queuet = Thread(target=self.queue_thread)
            self.queuet.daemon = True
            self.queuet.start()

flood_protect = flood_protect_class()

class connection_wrapper(object):
    def __init__(self, connection, config, flood_protection, bot_class, requires):
        self.irc=connection
        self.flood_protection = flood_protection
        self.config = config
        self.db = thingdb.thing
        self.bot=bot_class
        #self.r = require_class(requires)
        requirements = {}
        for require in requires:
            requirements[require] = importlib.import_module(require)
        self.r = other.toClass(requirements)
    def send(self, raw):
        if not self.flood_protection:
            self.irc.send("{}\r\n".format(raw))#.encode("UTF-8"))
        else:
            flood_protect.queue_add(self.irc, "{}\r\n".format(raw))#.encode("UTF-8"))
    def msg(self, channel, message):
        #self.send("PRIVMSG {} :{}".format(channel, message))
        if channel is not None:
            MSGLEN = 459 - 10 - len(channel)
            message_byte_count = sys.getsizeof(message)-37
            strings = [message[i:i+MSGLEN] for i in range(0, message_byte_count, MSGLEN)]
            for message in strings:
                self.send("PRIVMSG {} :{}".format(channel, message))
    def msg_first(self, channel, message):
        #self.send("PRIVMSG {} :{}".format(channel, message))
        if channel is not None:
            MSGLEN = 459 - 10 - len(channel)
            message_byte_count = sys.getsizeof(message)-37
            strings = [message[i:i+MSGLEN] for i in range(0, message_byte_count, MSGLEN)][::-1]
            for message in strings:
                flood_protect.queue_add_first(self.irc, "PRIVMSG {} :{}\r\n".format(channel, message))
    def notice(self, user, message):
        self.send("NOTICE {} :{}".format(user, message))
    def quit(self, message=""):
        self.send("QUIT :"+message)
    def ctcp(self, user, message):
        self.send("PRIVMSG {} :\x01{}\x01\x01".format(user, message))
    def flush(self):
        size = len(flood_protect.irc_queue)
        flood_protect.__init__()
        return str(size)
    def part(self,chan):
        self.irc.send("PART {0}\n".format(chan).encode('utf-8'))
    def nick(self,nick):
        self.irc.send("NICK {0}\n".format(nick).encode('utf-8'))
    def join(self,chan):  
        self.irc.send("JOIN {0}\n".format(chan).encode('utf-8'))
    def invite(self, chan, user):
        self.irc.send("INVITE {} {}\n".format(user, chan).encode("utf-8"))
    def action(self,channel,message):
        self.sendmsg(channel,"\x01ACTION " + message + "\x01")
    def kick(self,channel,user,message):
        user = user.replace(" ","").replace(":","")
        self.irc.send("KICK " + channel + " " + user+ " :" + message +"\r\n")
    def op(self,channel,nick):
        self.irc.send("MODE {0} +o {1}\n".format(channel,nick).encode('utf-8'))
    def deop(self,channel,nick):
        self.irc.send("MODE {0} -o {1}\n".format(channel,nick).encode('utf-8'))
    def ban(self,channel,nick):
        self.irc.send("MODE {0} +b {1}\n".format(channel,nick).encode('utf-8'))
    def unban(self,channel,nick):
        self.irc.send("MODE {0} -b {1}\n".format(channel,nick).encode('utf-8'))
    def quiet(self,channel,nick):
        self.irc.send("MODE {0} +q {1}\n".format(channel,nick).encode('utf-8'))
    def unquiet(self,channel,nick):
        self.irc.send("MODE {0} -q {1}\n".format(channel,nick).encode('utf-8'))
    def unvoice(self,channel,nick):
        self.irc.send("MODE {0} -v {1}\n".format(channel,nick).encode('utf-8'))
    def voice(self,channel,nick):
        self.irc.send("MODE {0} +v {1}\n".format(channel,nick).encode('utf-8'))
    def mode(self,channel,nick,mode):
        self.irc.send("MODE {0} {1} {2}\n".format(channel,mode,nick).encode('utf-8'))
