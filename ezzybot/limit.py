from .util import bucket as tokenbucket
from . import wrappers

class Limit(object):
    '''Limits the use of commands'''
    def __init__(self, command_limiting_initial_tokens, command_limiting_message_cost, command_limiting_restore_rate, override, permissions):
        """limit(20, 4, 0.13, ["admin"], {"admin": "user!*@*"})

        Limits the use of commands

        Arguments:
            command_limiting_initial_tokens {Integer} -- Initial tokens for tokenbucket
            command_limiting_message_cost {Integer} -- Message cost for tokenbucket
            command_limiting_restore_rate {Integer} -- Restore rate for token bucket
            override {List} -- List of permissions to override the limit
            permissions {Dict} -- All of the bots permissions.
        """
        self.command_limiting_initial_tokens = command_limiting_initial_tokens
        self.command_limiting_message_cost = command_limiting_message_cost
        self.command_limiting_restore_rate = command_limiting_restore_rate
        self.buckets = {}
        self.permissions = wrappers.permissions_class(permissions)
        self.override = override

    def command_limiter(self, info):
        #Check if admin/whatever specified
        if self.permissions.check(self.override, info.mask):
            return True
        if info.nick not in self.buckets:
            bucket = tokenbucket.TokenBucket(self.command_limiting_initial_tokens, self.command_limiting_restore_rate)
            self.buckets[info.nick] = bucket
        else:
            bucket = self.buckets[info.nick]

        if bucket.consume(self.command_limiting_message_cost):
            return True

        return False
