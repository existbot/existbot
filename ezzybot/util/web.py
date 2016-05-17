import requests

def paste(string):
    '''Returns a haste bin URL with the string pasted in it'''
    return "http://hastebin.com/"+requests.post("http://hastebin.com/documents", data=string).json()['key']