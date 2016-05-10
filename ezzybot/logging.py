from time import strftime
import os

def check_dir(path):
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path))

class log(object):
    def __init__(self, config=None, write_log=True, log_file=None):
        if log_file is not None:
            self.logging_file = log_file
        else:
            self.logging_file = os.path.join("data", config.host, config.nick.lower(), "")
        self.write_log = write_log
        check_dir(self.logging_file)
        
    def error(self, message):
        message = message.encode("UTF-8", "ignore")
        message = strftime("[%m/%d/%Y][%H:%M:%S][ERROR] {0}".format(message))
        print(message)
        self.write(message)
    
    def debug(self, message):
        message = message.encode("UTF-8", "ignore")
        message = strftime("[%m/%d/%Y][%H:%M:%S][DEBUG] {0}".format(message))
        print(message)
        self.write(message)
    
    def send(self, message):
        message = message.encode("UTF-8", "ignore")
        message = strftime("[%m/%d/%Y][%H:%M:%S][SEND] {0}".format(message))
        print(message)
        self.write(message)
    
    def receive(self, message):
        message = message.encode("UTF-8", "ignore")
        message = strftime("[%m/%d/%Y][%H:%M:%S][RECV] {0}".format(message))
        print(message)
        self.write(message)
    
    def write(self, message):
        if self.write_log:
            if message.replace(" ","").replace("\n","") != "":
                with open(os.path.join(self.logging_file, "bot.log"), "a") as log:
                    log.write(message.replace("\n","") + "\n")
                    log.close()
                    
