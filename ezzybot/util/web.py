import requests

def paste(string):
    return "http://hastebin.com/"+requests.post("http://hastebin.com/documents", data=string).json()['key']
