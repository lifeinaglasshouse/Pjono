from Pjono.Response import Http_Response

class Cookie(Http_Response):
    """
    Cookie class
    
    set or get client cookie
    """
    def __init__(self, headers: dict={}, content=None, HTTP: str="HTTP/1.1", status_code=(200, "OK"), **cookies):
        self.cookies = [f"{k}={v}" for k, v in cookies.items()]
        super().__init__(headers={**headers, "Set-Cookie":self.cookies}, content=content, HTTP=HTTP, status_code=status_code)
    
    @staticmethod
    def get(request: dict):
        """
        Get client cookie
        
        ## Return:
        dict
        """
        result = {}
        if "Cookie" in request["Headers"]:
            cookie = request["Headers"]["Cookie"]
            if "; " in cookie:
                for ck in cookie.split("; "):
                    ck = ck.split("=")
                    result[ck[0]] = ck[1]
            else:
                if ";" in cookie:
                    for ck in cookie.split(";"):
                        ck = ck.split("=")
                        result[ck[0]] = ck[1]
                else:
                    ck = cookie.split("=")
                    result[ck[0]] = ck[1]
        return result
    
    @staticmethod
    def set_attr(**kwargs):
        """
        Set cookie attribute.
        ```py
        cookie = Cookie(token="NkncP.0029psWefd-apq"+Cookie.set_attr(Secure=None, HttpOnly=None))
        # token=NkncP.0029psWefd-apq; Secure; HttpOnly
        ```
        """
        attribute = "; "+"; ".join([f"{k}{'='+v if v else ''}" for k, v in kwargs.items()])
        return attribute