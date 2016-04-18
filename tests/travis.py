#travis.py
import ezzybot, threading, time
mybot = ezzybot.bot()
config = {"channels":["#ezzybot-debug"], "nick": "EzzyBot-Travis"}
def runbot():
    mybot.run(config)

t = threading.Thread(target=runbot)
t.daemon=True
t.start()
time.sleep(20)
mybot.irc.send("PRIVMSG #ezzybot-debug :{0}Travis Testing script successful!\r\n".format(mybot.colours.CYAN))
mybot.irc.send("PART #ezzybot-debug\r\n")
time.sleep(1)
exit()
