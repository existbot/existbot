import thingdb
from fnmatch import fnmatch
from Queue import Queue
from threading import Thread
from time import sleep
import sys

log=None

def specify(local_log):
    global log
    log = local_log

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


class connection_wrapper(object):
    def __init__(self, connection, config, flood_protection, bot_class):
        self.irc=connection
        self.flood_protection = flood_protection
        self.config = config
        self.db = thingdb.thing
        self.bot=bot_class
    def send(self, raw):
        if self.flood_protection==False:
            self.irc.send("{0}\r\n".format(raw))#.encode("UTF-8"))
        else:
            flood_protect.queue_add(self.irc, "{0}\r\n".format(raw))#.encode("UTF-8"))
    def msg(self, channel, message):
        #self.send("PRIVMSG {} :{}".format(channel, message))
        MSGLEN = 459 - 10 - len(channel)
        message_byte_count = sys.getsizeof(message)-37
        strings = [message[i:i+MSGLEN] for i in range(0, message_byte_count, MSGLEN)]
        for message in strings:
            self.send("PRIVMSG {0} :{1}".format(channel, message))
    def notice(self, user, message):
        self.send("NOTICE {0} :{1}".format(user, message))
    def quit(self, message=""):
        self.send("QUIT :"+message)
