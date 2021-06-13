from Pjono.PARSE.html import HTML
import os
import json

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
__ascii__ = json.load(open(os.path.join(__location__, "PARSE/ascii.json"), "r"))

class Http_Response():
    """
    Http_Response object for creating a http response
    
    `respond` attributes have the raw http response
    """
    def __init__(self, headers: dict, HTTP: str="HTTP/1.1", status_code=(200, "OK")):
        self.respond = f"{HTTP} {status_code[0]} {status_code[1]}"
        if "CONTENT" in headers.keys():
            content = headers["CONTENT"]
            if type(content) == HTML:
                content = content.content
            headers.pop("CONTENT")
            for i, v in headers.items():
                self.respond = self.respond + f"\n{i}: {v}"
            self.respond = f"{self.respond}\n\n"
            if type(content) == bytes:
                self.respond = self.respond.encode()
                self.respond += bytearray(content)
            else:
                self.respond = self.respond + content
        else:
            for i, v in headers.items():
                self.respond = self.respond + f"\n{i}: {v}"

class Http_File(Http_Response):
    """
    Http_File object for building a http response with file content.
    Used to creating http response with binary file
    """
    def __init__(self, path: str, content_type: str, attachment: bool=False, filename: str=None, headers: dict=None):
        try:
            self.content = open(path, "r").read()
        except UnicodeDecodeError:
            self.content = open(path, "rb").read()
        if headers:
            headers["CONTENT"] = self.content
            headers["Content-Type"] = content_type 
        else:
            headers = {
                "CONTENT": self.content,
                "Content-Type": content_type
            }
        if attachment:
            if filename:
                headers["Content-Disposition"] = f"attachment; filename={filename}"
            else:
                headers["Content-Disposition"] = f"attachment"
        super().__init__(headers)

class StatusCodeError(Exception):
    pass

class Http_Redirect(Http_Response):
    """
    Redirecting client to specific url with parameters or not
    """
    def __init__(self, Location: str, status_code=(302, "Found"), **params):
        self.location = Location
        if status_code > 399 or status_code < 300:
            raise StatusCodeError("Status code can't be lower or higher than 300")
        if params:
            self.location += "?"
            for k, v in params.items():
                value = v.replace(" ", "+")
                for hex, char in __ascii__.items():
                    if char.lower() in list("qwertyuiopasdfghjklzxcvbnm+.0987654321"):
                        continue
                    value = value.replace(char, hex)
                self.location += f"{k}={value}"
                if not list(params).index(k) >= len(params) - 1:
                    self.location += "&"
        super().__init__({"Location":self.location}, status_code=status_code)