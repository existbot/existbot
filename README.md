# ezzybot [![Build Status](https://travis-ci.org/ezzybot/ezzybot.svg?branch=master)](https://travis-ci.org/ezzybot/ezzybot) [![Codacy Badge](https://api.codacy.com/project/badge/grade/6f9c84a479754bbb945d6ac4cf4cdbb1)](https://www.codacy.com/app/me_64/ezzybot) [![PyPI](https://img.shields.io/pypi/dm/ezzybot.svg)](https://pypi.python.org/pypi/ezzybot) [![Code Issues](https://www.quantifiedcode.com/api/v1/project/736ed122f2cd4abea04a58bb7665e73b/badge.svg)](https://www.quantifiedcode.com/app/project/736ed122f2cd4abea04a58bb7665e73b) [![Code Health](https://landscape.io/github/ezzybot/ezzybot/master/landscape.svg?style=flat)](https://landscape.io/github/ezzybot/ezzybot/master)

EzzyBot is a IRC bot framework built in python.

Installation
```
pip install ezzybot
```

Or, install the development version

```
pip install git+https://github.com/ezzybot/ezzybot
```

Example of use:

```
import ezzybot

mybot = ezzybot.bot()

def hello(info=None, conn=None):
    return "Hello!"

mybot.assign(function=hello, help_text="Returns 'Hello!'", commandname="hello")
mybot.run({"channels":["#ezzybot"], "host": "irc.freenode.net", "port": 6697, "ssl": True, "nick": "EzzyBot"})
```

#[Wiki](https://github.com/ezzybot/ezzybot/wiki)

Devs are: zz, Bowserinator, BWBellairs

Wanna know more? (IRC) Freenode: #ezzybot
[![Visit our IRC Chat!](https://kiwiirc.com/buttons/chat.freenode.net/ezzybot.png)](https://kiwiirc.com/client/chat.freenode.net/?nick=ezzy|?&theme=cli#ezzybot)
