#travis.py
import ezzybot, threading, time, sys
mybot = ezzybot.bot()
config = {"channels":[], "nick": "EzzyBot-CI-"+str(sys.version.split(" ")[0].replace(".", "-")), "log_channel": "#ezzybot"}
t = threading.Thread(target=mybot.run, args=(config,))
t.daemon=True
t.start()
time.sleep(20)
mybot.log.debug("Testing script successful")
time.sleep(1)
exit()
