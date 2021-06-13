import socket
from typing import Union
from Pjono.PARSE.parse import parse_request, parse_br, parse_dynamic_url
from Pjono.Response import Http_File, Http_Response
import traceback
import datetime
import os
import json

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
                    path = self.add_file("/" + file, Http_File(file, content_type))
                    _fp.append(path)
        else:
            for file in fp:
                path = self.add_file("/" + file, Http_File(file, _check_content_type(file.split(".")[1])))
                _fp.append(path)
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
    
    def launch(self, debug: bool=False):
        """
        This is the main function for launching the server.
        
        if debug is true, it will show an error in the page if the server get any error even if you have register
        `ERROR` page.
        """
        print(f"• Server live on {self.host}")
        print(f"• Debug {debug}")
        print(f"• Server live since {datetime.datetime.now()}")
        self.server.listen(1)
        while True:
            conn, addr = self.server.accept()
            http = conn.recv(1024)
            try:
                json = parse_request(http_request=http.decode())
                if json:
                    if json["Page"] in self.pages:
                        page = self.pages[json["Page"]]
                        respond = self.pages[json["Page"]](json)
                        print(f"{addr[0]} Requested {json['Page']} - {datetime.datetime.now()}")
                    else:
                        if "404" in self.pages:
                            page = self.pages["404"]
                            respond = page(json)
                        else:
                            html = open(os.path.join(__location__, "PAGES/404.html"), "r").read()
                            respond = Http_Response(status_code=(404, "Not Found"), headers={"CONTENT":html})
                        print(f"{addr[0]} Requested {json['Page']} but didn't exist - {datetime.datetime.now()}")
                else:
                    continue
                if isinstance(respond, str):
                    conn.sendall(Http_Response({
                        "CONTENT": respond
                    }).respond.encode())
                elif isinstance(respond, bytes):
                    conn.sendall(Http_Response({
                        "CONTENT": respond
                    }).respond)
                elif hasattr(respond, "respond"):
                    if isinstance(respond.respond, bytes):
                        conn.sendall(respond.respond)
                    else:
                        conn.sendall(respond.respond.encode())
                conn.close()
            except Exception as Error:
                e = traceback.format_exc()
                print(e)
                if debug:
                    html = open(os.path.join(__location__, "PAGES/error.html"), "r").read().replace("{{-error-}}", parse_br(e))
                    respond = Http_Response(status_code=(500, "Server Error"), headers={"CONTENT":html})
                else:
                    if "ERROR" in self.pages:
                        page = self.pages["ERROR"]
                        respond = page(json, Error)
                    else:
                        html = open(os.path.join(__location__, "PAGES/error1.html"), "r").read()
                        respond = Http_Response(status_code=(500, "Server Error"), headers={"CONTENT":html})
                conn.sendall(respond.respond.encode())
                conn.close()
