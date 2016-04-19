<<<<<<< HEAD
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
    if callable(func):
        return wrapper(func)
    return wrapper
    
def trigger(func=None, **kwargs):
    def wrapper(func):
        func._trigger = kwargs.get("trigger", "PRIVMSG")
        func._event = "trigger"
        if not hasattr(func, '_thread'):
        	func._thread = False
        events.append(func)
    if callable(func):
        return wrapper(func)
    return wrapper
    
def regex(func=None, **kwargs):
    def wrapper(func):
        func._trigger = kwargs.get("regex")
        func._event = "regex"
        if not hasattr(func, '_thread'):
        	func._thread = False
        events.append(func)
    if callable(func):
        return wrapper(func)
    return wrapper
=======
import inspect, collections

commands = {}
regexs = []
triggers = []

def command(arg=None, **kwargs):
    args = {}
    def command_wrapper(func):
        args.setdefault('commandname', func.__name__)
        args.setdefault('function', func)
        args.setdefault('help', inspect.getdoc(func))
        args.setdefault('prefix', '!')
        args.setdefault('perms', 'all')
        args.setdefault('requires', [])
        args.update(kwargs)
        args.setdefault('fullcommand', args["prefix"]+args["commandname"])
        if not args["prefix"]+args["commandname"] in commands.keys():
            commands[args["prefix"]+args["commandname"]] = args
        return func
    if isinstance(arg, collections.Callable):
        return command_wrapper(arg)
    return command_wrapper
    
def regex(arg=None, **kwargs):
    args = {}
    def command_wrapper(func):
        args.setdefault('function', func)
        args.setdefault('requires', [])
        args.update(kwargs)
        if args not in regexs:
            regexs.append(args)
        return func
    if isinstance(arg, collections.Callable):
        return command_wrapper(arg)
    return command_wrapper
    
def trigger(arg=None, **kwargs):
    args= {}
    def command_wrapper(func):
        args.setdefault('function', func)
        args.setdefault('trigger', 'PRIVMSG')
        args.setdefault('requires', [])
        args.update(kwargs)
        if args not in triggers:
            triggers.append(args)
        return func
    if isinstance(arg, collections.Callable):
        return command_wrapper(arg)
    return command_wrapper

#@command
#def moo(conn, info): #MUTICOLORED MOOOOOOOOOOOS nice
#    """Returns moo<x>"""
#    return "\x02\x032mo{}".format("\x03{0}o".format(random.randint(1,15)) * random.randint(1, 25))
>>>>>>> upstream/master
    
def singlethread(func):
    func._thread = True
    return func
