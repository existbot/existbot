events = []

def help_bot(conn=None, info=None):
    """Shows help for commands"""
    #conn.bot.send("PRIVMSG #ezzybot :{} {}".format(conn, info))
    for command in [func for func in conn.bot.events if func._event == "command"]:
        if command._commandname == info.args.lstrip():
            conn.notice(info.nick, command._help)

setattr(help_bot, "_commandname", "help")
setattr(help_bot, "_prefix", "!")
setattr(help_bot, "_help", help_bot.__doc__)
setattr(help_bot, "_perms", "all")
setattr(help_bot, "_event", "command")
setattr(help_bot, "_thread", False)
events.append(help_bot)

def list_bot(conn=None, info=None):
    return " ".join([func._commandname for func in conn.bot.events if func._event == "command"])

setattr(list_bot, "_commandname", "list")
setattr(list_bot, "_prefix", "!")
setattr(list_bot, "_help", list_bot.__doc__)
setattr(list_bot, "_perms", "all")
setattr(list_bot, "_event", "command")
setattr(list_bot, "_thread", False)
events.append(list_bot)

def bot_quit(conn, info):
    conn.quit()

setattr(bot_quit, "_commandname", "quit")
setattr(bot_quit, "_prefix", "!")
setattr(bot_quit, "_help", bot_quit.__doc__)
setattr(bot_quit, "_perms", ["admin"])
setattr(bot_quit, "_event", "command")
setattr(bot_quit, "_thread", False)
events.append(bot_quit)

def flush(conn, info):
    return "Sucessfully flushed {0} lines.".format(conn.flush())

setattr(flush, "_commandname", "flush")
setattr(flush, "_prefix", "!")
setattr(flush, "_help", flush.__doc__)
setattr(flush, "_perms", ["admin"])
setattr(flush, "_event", "command")
setattr(flush, "_thread", False)
events.append(flush)
