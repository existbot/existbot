import socks

required = ["nick", "host", "port"]

class config(object):
    '''Config class for the bot'''
    def __init__(self, config):
        '''Takes dictionary and gets all information, if it is not in dictionary uses default'''
        self.host = config.get("host", "irc.freenode.net")
        self.port = config.get("port", 6667)
        self.ipv6 = config.get("IPv6", False)
        self.ssl = config.get("SSL", False)
        self.sasl = config.get("SASL", False)
        self.do_auth = config.get("do_auth", False)
        self.auth_pass = config.get("auth_pass")
        self.auth_user = config.get("auth_user")
        self.nick = config.get("nick", "EzzyBot")
        self.ident = config.get("ident", "EzzyBot")
        self.realname = config.get("realname", "EzzyBot: a simple python framework for IRC bots.")
        self.channels = config.get("channels", ["#EzzyBot"])
        self.analytics = config.get("analytics", True)
        self.quit_message = config.get("quit_message", "EzzyBot: a simple python framework for IRC bots.")
        self.flood_protection = config.get("flood_protection", True)
        self.permissions = config.get("permissions", {})
        self.proxy = config.get("proxy", False)
        self.proxy_type = config.get("proxy_type", "SOCKS5")
        self.proxy_host = config.get("proxy_host", "")
        self.proxy_port = config.get("proxy_port", 1080)
        self.proxy_type = {"SOCKS5": socks.SOCKS5, "SOCKS4": socks.SOCKS4}[self.proxy_type]
        self.log_channel = config.get("log_channel", "#ezzybot-debug")
        self.password = config.get("pass")
        self.fifo = config.get("fifo", True)
        self.command_limiting_initial_tokens = config.get("command_limiting_initial_tokens", 20)
        self.command_limiting_message_cost = config.get("command_limiting_message_cost", 4)
        self.command_limiting_restore_rate = config.get("command_limiting_restore_rate", 0.13)
        self.limit_override = config.get("limit_override", ["admin", "dev"])
        self.add_devs = config.get("add_devs", False)
        self.pingfreq = 60
        self.timeout = self.pingfreq * 2
