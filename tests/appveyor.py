import ezzybot, threading, time, sys
mybot = ezzybot.bot()
config = {"channels":["#ezzybot-debug"], "nick": "EzzyBot-AV-"+str(sys.version.split(" ")[0].replace(".", "-")), "log_channel": "#ezzybot"}
t = threading.Thread(target=mybot.run, args=(config,))
t.daemon=True
t.start()
time.sleep(20)
exit()
