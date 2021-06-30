import os, sys

class dbg:
    """
    Debugger for PjonoApp
    """
    
    location = os.path.basename(sys.argv[0])
        
    def __init__(self):
        self.config = {
            "debug":True,
            "prefix":f"[THREAD:{self.location}]",
        }

    def log(self, *msg):
        if self.config["debug"]:
            print(self.config["prefix"],*msg)
    
    def configure(self, **options):
        for option, value in options.items():
            self.config[option] = value