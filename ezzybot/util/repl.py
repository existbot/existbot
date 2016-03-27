import code, sys, colours #Kinda made by doge, thanks doge.

colours = colours.colours()

class Repl(code.InteractiveConsole):
    def __init__(self, conn):
        code.InteractiveConsole.__init__(self, {"conn": conn})
        self.conn = conn
        self.channel = None
        self.buf = ""

    def write(self, data):
        self.buf += str(data)

    def flush(self):
        lines=self.buf.split("\n")
        for line in lines:
            if self.channel != None:
                if line != "":
                    self.conn.msg(self.channel, "{}| {}".format(colours.LIGHTGREEN, line))
        self.buf = ""

    def run(self, channel, code):
        self.channel = channel
        sys.stdout = self
        self.push(code)
        sys.stdout = sys.__stdout__
        self.flush()

    def showtraceback(self):
        type, value, lasttb = sys.exc_info()
        self.conn.msg(self.channel, colours.RED+"{0}: {1}".format(type.__name__, value))

    def showsyntaxerror(self, filename):
        self.showtraceback()
