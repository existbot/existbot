# ezzybot
EzzyBot is a IRC bot framework built in python.
```python
from ezzybot import bot

config = {  
   "nick": "EzzyBot",
   "channels": ["#ezzybot", "#ezzybot-debug", "#ezzybot-bots"],
   "port": 6667,
   "SSL": False,
   "SASL": True,
   "do_auth": False,
   "auth_user": "ezzybot",
   "auth_pass": "<password>",
   "quit_message": "Default quit reason",
   "permissions": {
       "admin": ["*!ident@host"]
    },
    "log_channel": "#ezzybot-debug"
}

mybot = bot(config)

mybot.run()
```

Installation
```
sudo pip install ezzybot
```
