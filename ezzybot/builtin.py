from util import hook, colours, repl, web, other
import logging, wrappers, limit
import socks, re, json, traceback, time, socket, os, glob, importlib, requests, pkg_resources
def help_bot(conn=None, info=None):
    #conn.bot.send("PRIVMSG #ezzybot :{} {}".format(conn, info))
    for fullcommand, command in conn.bot.commands.iteritems():
        if command["commandname"] == info.args.lstrip():
            conn.notice(info.nick, " {} : {}".format(fullcommand, command['help']))
            #conn.msg(info['channel'], command['help'])
            
def list_bot(info=None, conn=None):
    return " ".join([conn.bot.commands[command]["commandname"] for command in conn.bot.commands.keys()])
    
def bot_quit(conn, info):
    conn.quit()
def flush(conn, info):
    return "Sucessfully flushed {} lines.".format(conn.flush())

commands = {}
commands["!help"] = {"function": help_bot, "help": "This command.", "prefix": "!", "commandname": "help", "perms": "all", "requires": []}
commands["!quit"] = {"function": bot_quit, "help": "Forces the bot :to quit", "prefix":"!", "commandname": "quit", "perms":["admin"], "requires": []}
commands["!list"] = {"function": list_bot, "help":"list : lists all commands", "prefix": "!", "commandname": "list", "perms": "all", "requires": []}
commands["!flush"] = {"function": flush, "help": "Flushes queue", "prefix":"!", "commandname": "flush", "perms":["admin"], "requires": []}
