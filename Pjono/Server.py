import socket
from Pjono.PARSE.parse import parse_request, parse_br, parse_dynamic_url
from Pjono.Response import Http_File, Http_Response
import traceback
import datetime
import os

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

#HTTP/1.1 200 OK
#Date: Mon, 27 Jul 2009 12:28:53 GMT
#Server: Apache/2.2.14 (Win32)
#Last-Modified: Wed, 22 Jul 2009 19:15:56 GMT
#Content-Length: 88
#Content-Type: text/html
#Connection: Close

class PjonoApp():
    
    def __init__(self, server: tuple[str, int]=("127.0.0.1", 5500)):
        self.host = f"http://{server[0]}:{server[1]}"
        self.pages = {}
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind(server)
    
    def register(self, location: str):
        def decorator(func):
            self.pages[location] = func
        return decorator

    def add_file(self, location: str, file: Http_File):
        self.pages[location] = lambda request: file
    
    def launch(self, debug: bool=False):
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
                        respond = self.pages[json["Page"]](json)
                        print(f"{addr[0]} Requested {json['Page']} - {datetime.datetime.now()}")
                    else:
                        url = parse_dynamic_url(json["Page"])
                        if url:
                            if url["Origin"] in self.pages:
                                json["Param"] = url["Param"]
                                json["Page"] = url["Origin"]
                                respond = self.pages[url["Origin"]](json)
                                print(f"{addr[0]} Requested {json['Page']} - {datetime.datetime.now()}")
                            else:
                                if "404" in self.pages.keys():
                                    respond = self.pages["404"](json)
                                else:
                                    html = open(os.path.join(__location__, "PAGES/404.html"), "r").read()
                                    respond = Http_Response(status_code=(404, "Not Found"), response_headers={"CONTENT":html})
                                print(f"{addr[0]} Requested {json['Page']} but didn't exist - {datetime.datetime.now()}")    
                        else:
                            if "404" in self.pages.keys():
                                respond = self.pages["404"](json)
                            else:
                                html = open(os.path.join(__location__, "PAGES/404.html"), "r").read()
                                respond = Http_Response(status_code=(404, "Not Found"), response_headers={"CONTENT":html})
                            print(f"{addr[0]} Requested {json['Page']} but didn't exist - {datetime.datetime.now()}")
                else:
                    continue
                if type(respond.respond) == bytes:
                    conn.sendall(respond.respond)
                else:
                    conn.sendall(respond.respond.encode())
                conn.close()
            except Exception as Error:
                e = traceback.format_exc()
                print(e)
                if debug:
                    html = open(os.path.join(__location__, "PAGES/error.html"), "r").read().replace("{{-error-}}", parse_br(e))
                    respond = Http_Response(status_code=(500, "Server Error"), response_headers={"CONTENT":html})
                else:
                    if "ERROR" in self.pages.keys():
                        respond = self.pages["ERROR"](json, Error)
                    else:
                        html = open(os.path.join(__location__, "PAGES/error1.html"), "r").read()
                        respond = Http_Response(status_code=(500, "Server Error"), response_headers={"CONTENT":html})
                conn.sendall(respond.respond.encode())
                conn.close()
