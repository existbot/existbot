from time import strftime
from datetime import datetime
import os
from util.colours import colours

colours = colours()

# Class logger for storing info as well as events to a text file
# Getting data will be done in the future
# ect | !getLog <timestamp> <timestamp>

class Logging(object):
    def __init__(self, log_channel, conn):
        self.localEvents = {} # Stores events from when the program was first started
        self.log_channel = log_channel
        self.conn = conn
    def error(self, error_msg, channel=None): # Sends a message before the bot shuts (ect) down becuase of a error | "[ERROR] Failed to connect"
        if channel==None:
            channel = self.log_channel
        print "{}[ERROR] {}".format(strftime("[%m/%d/%Y][%H:%M:%S]"), error_msg)
        self.conn.send("PRIVMSG {} :{}[ERROR] {}".format(channel, colours.RED, error_msg))
        self.log("[ERROR] {}".format(error_msg))
    
    def debug(self, debug_msg, channel=None): # Sends information to the user | "[DEBUG] Connecting to freenode
        if channel==None:
            channel = self.log_channel
        print "{}[DEBUG] {}".format(strftime("[%m/%d/%Y][%H:%M:%S]"), debug_msg)
        self.conn.send("PRIVMSG {} :{}[DEBUG] {}".format(channel, colours.BLUE, debug_msg))
        self.log("[DEBUG] {}".format(debug_msg))
    
    def send(self, send_msg): # Displays what the fraemwork sends to a server | "[SEND] channel :moo"
        print "{}[SEND] {}".format(strftime("[%m/%d/%Y][%H:%M:%S]"), send_msg)
        self.log("[SEND] {}".format(send_msg))
    
    def receive(self, receive_msg): # Displays what the framework receives | [RECV] channel nick :msg"
        print "{}[RECV] {}".format(strftime("[%m/%d/%Y][%H:%M:%S]"), receive_msg)
        self.log("[RECV] {}".format(receive_msg))
        
    def search(self,time1,time2=None):
        time1 = time1.replace("]["," ").replace("]","").replace("[","")
        if time2 != None:
            time2 = time2.replace("]["," ").replace("]","").replace("[","")

        FMT = '%m/%d/%Y %H:%M:%S'
        returned = []
        for key in self.localEvents:
            tdelta = datetime.strptime(time1, FMT) - datetime.strptime( key.replace("]["," ").replace("]","").replace("[","") , FMT)
            if tdelta.total_seconds() > 0:
                if time2 != None:
                    dif2 = datetime.strptime(time2, FMT) - datetime.strptime( key.replace("]["," ").replace("]","").replace("[","") , FMT)
                    if dif2.total_seconds() < 0:
                        returned.append(self.localEvents[key])
                else:
                    returned.append(self.localEvents[key])
        return returned
        #[03/15/2016][20:15:58] 
        
    
    def log(self, log_msg): # Logs a msg to a txt file with a timestamp
        compiled_msg = strftime("[%m/%d/%Y][%H:%M:%S] {}".format(log_msg))
        self.localEvents[strftime("[%m/%d/%Y][%H:%M:%S]")] = log_msg
        if compiled_msg.replace(" ","").replace("\n","") != "":
            with open(os.getcwd()+"/log.ezzy", "a") as logFile:
                logFile.write(compiled_msg.replace("\n","") + "\n")
