
class Http_Response():
    
    def __init__(self, HTTP: str="HTTP/1.1", *, status_code: tuple[int, str]=(200, "OK"), response_headers: dict):
        self.respond = f"{HTTP} {status_code[0]} {status_code[1]}"
        if "CONTENT" in response_headers.keys():
            content = response_headers["CONTENT"]
            response_headers.pop("CONTENT")
            for i, v in response_headers.items():
                self.respond = self.respond + f"\n{i}: {v}"
            self.respond = f"{self.respond}\n\n"
            if type(content) == bytes:
                self.respond = self.respond.encode()
                self.respond += bytearray(content)
            else:
                self.respond = self.respond + content
        else:
            for i, v in response_headers.items():
                self.respond = self.respond + f"\n{i}: {v}"

class Http_File(Http_Response):

    def __init__(self, path: str, content_type: str, attachment: bool=False, filename: str=None):
        try:
            self.content = open(path, "r").read()
        except UnicodeDecodeError:
            self.content = open(path, "rb").read()
        response_headers = {
            "CONTENT": self.content,
            "Content-Type": content_type
        }
        if attachment:
            if filename:
                response_headers["Content-Disposition"] = f"attachment; filename={filename}"
            else:
                response_headers["Content-Disposition"] = f"attachment"
        super().__init__(HTTP="HTTP/1.1", response_headers=response_headers)

class Http_Redirect(Http_Response):
    
    def __init__(self, Location: str, status_code=(302, "Found")):
        super().__init__(HTTP="HTTP/1.1", status_code=status_code, response_headers={"Location":Location})