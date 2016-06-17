from .bot import *

__version__ = "2.1.0-git"

def cmd():
    import argparse,json
    parser = argparse.ArgumentParser(description="Ezzybot "+__version__)
    parser.add_argument("-v","--version",action='version',version=__version__)
    parser.add_argument("-s","--start",help="Starts a ezzybot instance", type=json.loads, dest="json", required=True)
    args = parser.parse_args()
    bot(args.json).run()
