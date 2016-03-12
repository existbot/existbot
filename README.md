# ezzybot

EzzyBot is a IRC bot framework built in python.

Example of use:

```
import ezzybot

def hello(info=None, conn=None):
    return "Hello!"

ezzybot.assign(function=hello, help_text="Returns 'Hello!'", commandname="hello")
ezzybot.run({"channels":["#ezzybot"], "host": "irc.freenode.net", "port": 6697, "ssl": True, "nick": "EzzyBot"})
```



Devs are: zz, Bowserinator, BWBellairs

Wanna know more? (IRC) Freenode: #ezzybot
[![Visit our IRC Chat!](https://kiwiirc.com/buttons/chat.freenode.net/ezzybot.png)](https://kiwiirc.com/client/chat.freenode.net/?nick=ezzy|?&theme=cli#ezzybot)
