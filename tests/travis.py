#travis.py
import ezzybot, threading, time
mybot = ezzybot.bot()
def runbot():
    mybot.run({"channels":["#ezzybot"], "nick": "EzzyBot-Travis"})

t = threading.Thread(target=runbot)
t.daemon=True
t.start()
time.sleep(30)
exit()
