import collections

events = []

def command(func=None, **kwargs):
    def wrapper(func):
        func._commandname =  kwargs.get("commandname", func.__name__)
        func._help = func.__doc__
        func._prefix = kwargs.get("prefix", "!")
        func._perms = kwargs.get("perms", "all")
        func._event = "command"
        if not hasattr(func, '_thread'):
        	func._thread = False
        events.append(func)
    if isinstance(func, collections.Callable):
        return wrapper(func)
    return wrapper

def trigger(func=None, **kwargs):
    def wrapper(func):
        func._trigger = kwargs.get("trigger", "PRIVMSG")
        func._event = "trigger"
        if not hasattr(func, '_thread'):
        	func._thread = False
        events.append(func)
    if isinstance(func, collections.Callable):
        return wrapper(func)
    return wrapper

def regex(func=None, **kwargs):
    def wrapper(func):
        func._regex = kwargs.get("regex")
        func._event = "regex"
        if not hasattr(func, '_thread'):
        	func._thread = False
        events.append(func)
    if isinstance(func, collections.Callable):
        return wrapper(func)
    return wrapper

def singlethread(func):
    func._thread = True
    return func
