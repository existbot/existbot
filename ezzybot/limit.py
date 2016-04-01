from util import bucket as tokenbucket
import wrappers


class Limit(object):
    def __init__(self, command_limiting_initial_tokens, command_limiting_message_cost, command_limiting_restore_rate, override, permissions):
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
