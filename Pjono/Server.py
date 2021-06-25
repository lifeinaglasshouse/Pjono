import socket
from typing import Type
from Pjono.PARSE.parse import parse_request, parse_br
from Pjono.Response import Http_File, Http_Response
import traceback
import datetime
import os
import json
import threading, keyboard
import time

def handler_keyboardInterupt(hotkey: str):
    while True:
        if keyboard.is_pressed(hotkey):
            print("\nClosing Server")
            os._exit(0)

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

class PjonoApp():
    """
    PjonoApp object for creating a server.
    """
    def __init__(self, server=("127.0.0.1", 5500)):
        self.host = f"http://{server[0] if server[0] else 'localhost'}:{server[1]}"
        self.pages = {}
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind(server)

    def register(self, location: str, *variables: str):
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
            self.pages[location] = func, variables
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
    
    def _translate_var_url(self, url: str):
        for location in self.pages.keys():
            if url.startswith(location):
                if isinstance(self.pages[location], tuple):
                    arg = url.replace(location, "").split("/")[1:]
                    ind = self.pages[location][1]
                    return location, {ind[i]:arg[i] for i in range(len(ind))}
        return None

    def handle_client(self, conn, addr, debug):
        """
        Coroutine function for handling client
        """
        try:
            json = parse_request(http_request=conn.recv(1024).decode())
            if json:
                json["Variables"] = {}
                if json["Page"] in self.pages:
                    respond = self.pages[json["Page"]](json) if not isinstance(self.pages[json["Page"]], tuple) else self.pages[json["Page"]][0](json)
                    respond = Http_Response(content=respond) if not isinstance(respond, Http_Response) else respond
                    print(f"{self._get_time()} {addr[0]} Requested[{json['Method']}] {json['Page']} | ({respond.status_code[0]}|{respond.status_code[1]})")
                else:
                    try:
                        loc, vr = self._translate_var_url(json["Page"])
                    except TypeError:
                        loc = None
                    if loc:
                        json["Variables"] = vr
                        respond = self.pages[loc][0](json)
                        respond = Http_Response(content=respond) if not isinstance(respond, Http_Response) else respond
                        print(f"{self._get_time()} {addr[0]} Requested[{json['Method']}] {json['Page']} | ({respond.status_code[0]}|{respond.status_code[1]})")
                    else:
                        if "404" in self.pages:
                            respond = self.pages["404"](json) if not isinstance(self.pages["404"], tuple) else self.pages["404"][0](json)
                            respond = Http_Response(content=respond, status_code=(404, "Not Found")) if not isinstance(respond, Http_Response) else respond
                        else:
                            respond = Http_Response(status_code=(404, "Not Found"), content=open(os.path.join(__location__, "PAGES/404.html"), "r").read())
                        print(f"{self._get_time()} {addr[0]} Requested[{json['Method']}] {json['Page']} | ({respond.status_code[0]}|{respond.status_code[1]})")
            else:
                return
            conn.sendall(respond.respond if isinstance(respond.respond, bytes) else respond.respond.encode())
            conn.close()
        except Exception as Error:
            e = traceback.format_exc()
            print(e)
            if debug:
                html = open(os.path.join(__location__, "PAGES/error.html"), "r", encoding="utf-8").read().replace("{{-error-}}", parse_br(e))
                respond = Http_Response(status_code=(500, "Server Error"), content=html)
            else:
                if "ERROR" in self.pages:
                    respond = self.pages["ERROR"](json, Error) if not isinstance(self.pages[json["ERROR"]], tuple) else self.pages["ERROR"][0](json)
                    respond = Http_Response(content=respond) if not isinstance(respond, Http_Response) else respond
                else:
                    html = open(os.path.join(__location__, "PAGES/error1.html"), "r").read()
                    respond = Http_Response(status_code=(500, "Server Error"), content=html)
            conn.sendall(respond.respond if isinstance(respond.respond, bytes) else respond.respond.encode()) 
            conn.close()
    
    def launch(self, debug: bool=False, end_hotkey=["ctrl","alt","c"], sleep: float=0.2):
        """
        launching the server. if debug true, it will display the error in the page. sleep is for
        how long the server should sleep after create a new thread for handling client. If sleep argument set
        to `0.0`, the cpu usage may be high. Recommended to set it as default. end_hotkey is for which hotkey should end
        the server.
        """
        times = datetime.datetime.now()
        print(f"• Server live on {self.host}")
        print(f"• Debug: {debug}")
        print(f"• Server live since [{times.day}/{times.month}/{times.year}|{times.hour}:{times.minute}:{times.second}]")
        print(f"Press {'+'.join(end_hotkey).upper()} to end the server")
        threading.Thread(target=handler_keyboardInterupt, args=("+".join(end_hotkey),)).start() # Listen to "end_hotkey" hotkey
        self.server.listen(1)
        while True:
            conn, addr = self.server.accept()
            threading.Thread(target=self.handle_client, args=(conn, addr, debug)).start() # create new thread to handle client
            time.sleep(sleep) # To reduce cpu usage(its not always going to work but still gonna use it)