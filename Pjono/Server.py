from Pjono.PARSE.Html import HTML
from Pjono.PARSE.Components import HtComponents
import socket
import sys
from Pjono.PARSE.parse import parse_request, parse_br
from Pjono.Response import Http_File, Http_Response
import traceback
import datetime
import os
import json
import threading
import time
from Pjono.Debug import dbg

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

__mimetype__ = json.load(open(os.path.join(__location__, "mime.json")))

#HTTP/1.1 200 OK
#Date: Mon, 27 Jul 2009 12:28:53 GMT
#Server: Apache/2.2.14 (Win32)
#Last-Modified: Wed, 22 Jul 2009 19:15:56 GMT
#Content-Length: 88
#Content-Type: text/html
#Connection: Close

def _get_files_in_dir(path: str):
    result = []
    for path, dirname, files in os.walk(path):
        dirname # my vscode keep highlighting dirname as unused variable. Its just annoying
        for name in files:
            result.append(os.path.join(path, name).replace("\\", "/"))
    return result

def _check_content_type(media_format: str):
    if media_format in __mimetype__:
        return __mimetype__[media_format]
    else:
        return f"text/{media_format}"

_debug = dbg()

class PjonoApp():
    """
    PjonoApp object for creating a server.
    """
    
    ROOT = "/"
    ERROR = "ERROR"
    _404 = "404"
    
    def __init__(self, name:str, server=("127.0.0.1", 5500)):
        self.name = name
        self.host = f"http://{server[0] if server[0] else 'localhost'}:{server[1]}"
        self.pages = {
            self.ROOT: lambda r: HTML(os.path.join(__location__, "PAGES/start.html"), {"{-NAME-}":self.name})
        }
        self.add_file("/Pjono/PAGES/Assets/icon.png", Http_File(os.path.join(__location__, "PAGES/Assets/icon.png"), "image/png"))
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.settimeout(1.0)
        self.server.bind(server)

    def register(self, location: str):
        """
        (This is decorator function)
        Register a server location:
        - root: `/`
        - 404 Error: `404`
        - 500 Server Error: `ERROR`
        
        return dict to func argument. Make sure to add one argument to your
        function
        
        the dict argument contain:
        - Method: str
        - Page: str
        - Http: str
        - Headers: dict
        - Form: dict
        - Param: dict
        """
        def decorator(func):
            self.pages[location] = func
        return decorator

    def add_file(self, location: str, file: Http_File):
        """
        Adding specific file to server. If you want to add files inside specific directory,
        you can use `add_folder` function instead
        """
        self.pages[location] = lambda request: file
        return location

    def add_folder(self, directory: str, only_type: str=None):
        """
        Add files in specific directory. This function for adding css, image, js and much more.
        For specific file, use `add_file` function. Will return all the file paths that have been added in tuple
        """
        fp = _get_files_in_dir(directory)
        _fp = []
        if only_type:
            content_type = _check_content_type(only_type)
            for file in fp:
                if file.endswith(f".{only_type}"):
                    _fp.append(self.add_file("/" + file, Http_File(file, content_type)))
        else:
            for file in fp:
                _fp.append(self.add_file("/" + file, Http_File(file, _check_content_type(file.split(".")[1]))))
        return tuple(_fp)
    
    def remove_files(self, paths):
        """
        Remove file from specific path
        """
        if isinstance(paths, str):
            self.pages.pop(paths)
        else:
            for path in paths:
                self.pages.pop(path)
        
    def reload_files(self, paths):
        """
        Reload files from specific path. Recommended to use it when necessarry such as editing css file while the server run
        """
        if isinstance(paths, str):
            if paths.startswith("/"):
                _path = paths[1:]
            self.add_file(paths, Http_File(_path, _check_content_type(_path[_path.index(".")+1:])))
        else:
            for path in paths:
                if path.startswith("/"):
                    _path = path[1:]
                self.add_file(path, Http_File(_path, _check_content_type(_path[_path.index(".")+1:])))
    
    def _get_time(self):
        time = datetime.datetime.now()
        return f"[{time.hour}:{time.minute}:{time.second}]"
    
    def check_var_url(self, url: str):
        _debug.log("Checking url if url is variable url")
        for location in self.pages.keys():
            if "{" in location and "}" in location:
                loc = location.split("/{")[0]
                if url.startswith(loc):
                    _debug.log("Found one location",location)
                    return location
        _debug.log("Doesn't found anything")
        return None
    
    def get_var(self, origin: str, url: str):
        _debug.log("Getting variable from variable url")
        _debug.log("Initiliaze\n", "Origin:", origin, "Client Url:", url)
        url = url.split("/")
        origin = origin.split("/")
        result = {}
        for i in range(len(origin)):
            try:
                if url[i] == origin[i]:
                    _debug.log(url[i], "is", origin[i])
                    pass
                else:
                    if origin[i].startswith("{") and origin[i].endswith("}"):
                        _debug.log("Found variable", origin[i], url[i])
                        result[origin[i][1:-1]] = url[i]
                    else:
                        _debug.log("Detecting 404")
                        return None
            except IndexError:
                _debug.log("Detecting 404")
                return None
        _debug.log("Return Result", result)
        return result

    def check_respond(self, respond, status_code=(200,"OK")):
        return Http_Response(content=respond, status_code=status_code) if not isinstance(respond, Http_Response) else respond

    def handle_client(self, conn, addr, debug):
        """
        function for handling client
        """
        _debug.log("handling",addr)
        try:
            _debug.log("Parse Request")
            json = parse_request(http_request=conn.recv(1024).decode())
            if json:
                _debug.log("Succesfully Parsing", json)
                if json["Page"] in self.pages:
                    _debug.log("Found page", json["Page"], "\nCreating Respond")
                    respond = self.pages[json["Page"]](json)
                    respond = self.check_respond(respond)
                    print(f"{self._get_time()} {addr[0]} Requested[{json['Method']}] {json['Page']} | ({respond.status_code[0]}|{respond.status_code[1]})")
                else:
                    _debug.log("Page not found but it may be a variable url", json["Page"])
                    page = self.check_var_url(json["Page"])
                    var = self.get_var(page, json["Page"]) if page else None
                    if var:
                        _debug.log(json["Page"], "is a variable url", "\nCreating Respond")
                        respond = self.pages[page](json, **var)
                        respond = self.check_respond(respond)
                        print(f"{self._get_time()} {addr[0]} Requested[{json['Method']}] {json['Page']} | ({respond.status_code[0]}|{respond.status_code[1]})")
                    else:
                        _debug.log("Page is actually doesn't exist", json["Page"])
                        if "404" in self.pages:
                            _debug.log("Get 404 page from Server")
                            respond = self.pages["404"](json)
                            respond = self.check_respond(respond, status_code=(404, "Not Found"))
                        else:
                            _debug.log("Get 404 page template")
                            respond = Http_Response(status_code=(404, "Not Found"), content=open(os.path.join(__location__, "PAGES/404.html"), "r").read())
                        print(f"{self._get_time()} {addr[0]} Requested[{json['Method']}] {json['Page']} | ({respond.status_code[0]}|{respond.status_code[1]})")
            else:
                return
            conn.sendall(respond.respond if isinstance(respond.respond, bytes) else respond.respond.encode())
            conn.close()
            _debug.log("Closing Connection from", addr)
        except Exception as Error:
            _debug.log("Error Occured")
            e = traceback.format_exc()
            print(e)
            if debug:
                html = open(os.path.join(__location__, "PAGES/error.html"), "r", encoding="utf-8").read().replace("{{-error-}}", parse_br(e))
                respond = Http_Response(status_code=(500, "Server Error"), content=html)
            else:
                if "ERROR" in self.pages:
                    respond = self.pages["ERROR"](json, Error)
                    respond = self.check_respond(respond, status_code=(500, "Server Error"))
                else:
                    html = open(os.path.join(__location__, "PAGES/error1.html"), "r").read()
                    respond = Http_Response(status_code=(500, "Server Error"), content=html)
            conn.sendall(respond.respond if isinstance(respond.respond, bytes) else respond.respond.encode()) 
            conn.close()
    
    def launch(self, debug: bool=False, sleep: float=0.2, debug_print:bool=False):
        """
        launching the server. if debug true, it will display the error in the page. sleep is for
        how long the server should sleep after create a new thread for handling client. If sleep argument set
        to `0.0`, the cpu usage may be high. Recommended to set it as default. debug_print is for logging the Server
        process.
        """
        times = datetime.datetime.now()
        print(f"• {self.name} live on {self.host}")
        print(f"• Debug: {debug}")
        print(f"• Server live since [{times.day}/{times.month}/{times.year}|{times.hour}:{times.minute}:{times.second}]")
        print("Press CTRL+C to end the server")
        self.server.listen(1)
        _debug.configure(debug=debug_print)
        try:
            while True:
                conn = None
                try:
                    conn, addr = self.server.accept()
                    _debug.log("Accept Connection from", addr)
                except socket.timeout:
                    pass
                else:
                    _debug.log("Creating new thread for", addr)
                    threading.Thread(target=self.handle_client, args=(conn, addr, debug)).start() # create new thread to handle client
                    time.sleep(sleep) # To reduce cpu usage(its not always going to work but still gonna use it)
        except KeyboardInterrupt:
            _debug.log("Keyboard Interrupt")
            if conn:
                _debug.log("Connection exist, closing")
                conn.close()
            print("Closing Server")
            sys.exit(0)