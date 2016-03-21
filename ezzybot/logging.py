from time import strftime
from datetime import datetime
import os
from colours import colours

colours = colours()

# Class logger for storing info as well as events to a text file
# Getting data will be done in the future
# ect | !getLog <timestamp> <timestamp>

class Logging(object):
    def __init__(self, log_channel, conn):
        self.localEvents = {} # Stores events from when the program was first started
        self.log_channel = log_channel
        self.conn = conn
    def error(self, error_msg): # Sends a message before the bot shuts (ect) down becuase of a error | "[ERROR] Failed to connect"
        print "{0}[ERROR] {1}".format(strftime("[%m/%d/%Y][%H:%M:%S]"), error_msg)
        self.conn.send("PRIVMSG {0} :{1}[ERROR] {2}".format(self.log_channel, colours.RED, error_msg))
        self.log("[ERROR] {0}".format(error_msg))
    
    def debug(self, debug_msg): # Sends information to the user | "[DEBUG] Connecting to freenode
        print "{0}[DEBUG] {1}".format(strftime("[%m/%d/%Y][%H:%M:%S]"), debug_msg)
        self.conn.send("PRIVMSG {0} :{1}[DEBUG] {2}".format(self.log_channel, colours.BLUE, debug_msg))
        self.log("[DEBUG] {0}".format(debug_msg))
    
    def send(self, send_msg): # Displays what the fraemwork sends to a server | "[SEND] channel :moo"
        print "{0}[SEND] {1}".format(strftime("[%m/%d/%Y][%H:%M:%S]"), send_msg)
        self.log("[SEND] {0}".format(send_msg))
    
    def receive(self, receive_msg): # Displays what the framework receives | [RECV] channel nick :msg"
        print "{0}[RECV] {1}".format(strftime("[%m/%d/%Y][%H:%M:%S]"), receive_msg)
        self.log("[RECV] {0}".format(receive_msg))
        
    def search(self,time1,time2=None):
        time1 = time1.replace("]["," ").replace("]","").replace("[","")
        if time2 is not None:
            time2 = time2.replace("]["," ").replace("]","").replace("[","")

        FMT = '%m/%d/%Y %H:%M:%S'
        returned = []
        for key in self.localEvents:
            tdelta = datetime.strptime(time1, FMT) - datetime.strptime( key.replace("]["," ").replace("]","").replace("[","") , FMT)
            if tdelta.total_seconds() > 0:
                if time2 is not None:
                    dif2 = datetime.strptime(time2, FMT) - datetime.strptime( key.replace("]["," ").replace("]","").replace("[","") , FMT)
                    if dif2.total_seconds() < 0:
                        returned.append(self.localEvents[key])
                else:
                    returned.append(self.localEvents[key])
        return returned
        #[03/15/2016][20:15:58] 
        
    
    def log(self, log_msg): # Logs a msg to a txt file with a timestamp
        compiled_msg = strftime("[%m/%d/%Y][%H:%M:%S] {0}".format(log_msg))
        self.localEvents[strftime("[%m/%d/%Y][%H:%M:%S]")] = log_msg
        if compiled_msg.replace(" ","").replace("\n","") != "":
            with open(os.getcwd()+"/log.ezzy", "a") as logFile:
                logFile.write(compiled_msg.replace("\n","") + "\n")
