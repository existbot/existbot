import inspect

global commands, regexs, triggers

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
        commands[args["prefix"]+args["commandname"]] = args
        return func
    if callable(arg):
        return command_wrapper(arg)
    return command_wrapper
    
def regex(arg=None, **kwargs):
    args = {}
    def command_wrapper(func):
        args.setdefault('function', func)
        args.setdefault('requires', [])
        args.update(kwargs)
        regexs.append(args)
        return func
    if callable(arg):
        return command_wrapper(arg)
    return command_wrapper
    
def trigger(arg=None, **kwargs):
    args= {}
    def command_wrapper(func):
        args.setdefault('function', func)
        args.setdefault('trigger', 'PRIVMSG')
        args.setdefault('requires', [])
        args.update(kwargs)
        triggers.append(args)
        return func
    if callable(arg):
        return command_wrapper(arg)
    return command_wrapper

#@command
#def moo(conn, info): #MUTICOLORED MOOOOOOOOOOOS nice
#    """Returns moo<x>"""
#    return "\x02\x032mo{}".format("\x03{0}o".format(random.randint(1,15)) * random.randint(1, 25))
    
#print commands
