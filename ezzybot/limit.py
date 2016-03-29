from util import bucket as tokenbucket


class Limit(object):
    def __init__(self, command_limiting_initial_tokens=20, command_limiting_message_cost=4, command_limiting_restore_rate=0.13):
        self.command_limiting_initial_tokens = command_limiting_initial_tokens
        self.command_limiting_message_cost = command_limiting_message_cost
        self.command_limiting_restore_rate = command_limiting_restore_rate
        self.buckets = {}
    def command_limiter(self, info):
        if info.nick not in self.buckets:
            bucket = tokenbucket.TokenBucket(self.command_limiting_initial_tokens, self.command_limiting_restore_rate)
            self.buckets[info.nick] = bucket
        else:
            bucket = self.buckets[info.nick]
    
        if bucket.consume(self.command_limiting_message_cost):
            return True
    
        return False
