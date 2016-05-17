import thingdb
from fnmatch import fnmatch
from threading import Thread
from time import sleep, time
from .util import other
import sys
import importlib

class permissions_class(object):
    '''Checks if someone has valid permissions'''
    def __init__(self, permissions):
        self.permissions = permissions # {"admin": "zz!*@*"}

    def check(self, perms, mask): # perms = # ["admin"]
        '''Takes list and checks if they have valid permissions'''
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

    def __init__(self, bot_class):
        self.irc=bot_class.socket
        self.flood_protection = bot_class.config.flood_protection
        self.config = bot_class.config
        self.db = thingdb.thing
        self.bot=bot_class

    def send(self, raw):
        if not self.flood_protection:
            self.irc.send("{0}\r\n".format(raw).encode("UTF-8"))
        else:
            flood_protect.queue_add(self.bot, "{0}\r\n".format(raw).encode("UTF-8"))

    def msg(self, channel, message):
        #self.send("PRIVMSG {} :{}".format(channel, message))
        if channel is not None:
            MSGLEN = 459 - 10 - len(channel)
            message_byte_count = sys.getsizeof(message)-37
            strings = [message[i:i+MSGLEN] for i in range(0, message_byte_count, MSGLEN)]
            for message in strings:
                self.send("PRIVMSG {0} :{1}".format(channel, message))

    def msg_first(self, channel, message):
        #self.send("PRIVMSG {} :{}".format(channel, message))
        if channel is not None:
            MSGLEN = 459 - 10 - len(channel)
            message_byte_count = sys.getsizeof(message)-37
            strings = [message[i:i+MSGLEN] for i in range(0, message_byte_count, MSGLEN)][::-1]
            for message in strings:
                flood_protect.queue_add_first(self.irc, "PRIVMSG {0} :{1}\r\n".format(channel, message))

    def notice(self, user, message):
        self.send("NOTICE {0} :{1}".format(user, message))

    def quit(self, message=""):
        self.send("QUIT :"+message)
    
    def ctcp(self, user, message):
        self.send("PRIVMSG {0} :\x01{1}\x01\x01".format(user, message))

    def flush(self):
        size = len(flood_protect.irc_queue)
        flood_protect.__init__()
        return str(size)

    def ping(self):
        self.send("PING :{}".format(str(int(time()))).encode('utf-8'))

    def part(self, chan):
        self.send("PART {0}".format(chan))

    def nick(self, nick):
        self.send("NICK {0}".format(nick))

    def join(self, chan):
        self.send("JOIN {0}".format(chan))

    def invite(self, chan, user):
        self.send("INVITE {0} {1}".format(user, chan))

    def action(self, channel, message):
        self.sendmsg(channel,"\x01ACTION " + message + "\x01")

    def kick(self,channel, user, message):
        user = user.replace(" ","").replace(":","")
        self.send("KICK " + channel + " " + user+ " :" + message)

    def op(self, channel, nick):
        self.send("MODE {0} +o {1}".format(channel, nick))

    def deop(self, channel, nick):
        self.send("MODE {0} -o {1}".format(channel, nick))

    def ban(self, channel, nick):
        self.send("MODE {0} +b {1}".format(channel, nick))

    def unban(self, channel, nick):
        self.send("MODE {0} -b {1}".format(channel, nick))

    def quiet(self, channel, nick):
        self.send("MODE {0} +q {1}".format(channel, nick))

    def unquiet(self, channel, nick):
        self.send("MODE {0} -q {1}".format(channel, nick))

    def unvoice(self, channel, nick):
        self.send("MODE {0} -v {1}".format(channel, nick))

    def voice(self, channel, nick):
        self.send("MODE {0} +v {1}".format(channel, nick))

    def mode(self, channel, nick, mode):
        self.send("MODE {0} {1} {2}".format(channel, mode, nick))
