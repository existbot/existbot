import importlib
#Plugin. Each plugin will be under a plugins folder
class Plugin(object):
    def __init__(self,url,name=None,functionName=None): 
        #url, Ie, "plugins/calc", the folder url, 
        #name=folder name, ie calc
        #functionName = name of command to be passed, ie calc (Gets run in !calc)
        name = url.split("/")[-1].split(":")[0]
        functionName = url.split(":")[1]
        self.url = url
        self.name = "plugins."+name
        self.functionName = functionName
        self.function = None
    
    def load(self):
        result = __import__(self.name)
        try:
            self.function = getattr(result,self.name.split(".")[-1])
            self.function = getattr(self.function,self.functionName)
        except:
            raise Exception("Could not find function {0} in plugin {1}".format(self.functionName,self.name))
    
    def reload(self): #Replaces self.function with updated, re imports module
        result = reload(importlib.import_module(self.name))
        #try:
        
        self.function = getattr(result,self.functionName)
        #self.function = getattr(self.function,self.functionName)
        #except:
            #raise Exception("Could not find function {0} in plugin {1}".format(self.functionName,self.name))
