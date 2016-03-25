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
        args.update(kwargs)
        tirggers.append(args)
        return func
    if callable(arg):
        return command_wrapper(arg)
    return command_wrapper
