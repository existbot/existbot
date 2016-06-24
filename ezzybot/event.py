class Event(object):

    def __init__(self, raw):
        self.raw = raw
        if raw.startswith(":"):
            raw = raw.replace(":", "", 1)
            self.source, self.type, self.target, args = raw.split(" ", 3)
        else:
            self.type, args = raw.split(" ", 1)
            self.source = self.target = None
        self.arguments = []
        args = args.split(":", 1)
        for arg in args[0].split(" "):
            if len(arg) > 0:
                self.arguments.append(arg)
        if len(args) > 1:
            self.arguments.append(args[1])
