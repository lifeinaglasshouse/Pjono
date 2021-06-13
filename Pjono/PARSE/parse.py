import os
import json

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
__ascii__ = json.load(open(os.path.join(__location__, "ascii.json"), "r"))

def parse_request(http_request: str):
    """
    This function is for parsing the http request:
    
    Example http request:\n
    ```
    GET /index.html HTTP/1.1
    User-Agent: Mozilla/4.0 (compatible; MSIE5.01; Windows NT)
    Host: www.example.com
    Accept-Language: en-us
    Accept-Encoding: gzip, deflate
    Connection: Keep-Alive
    ```
    It will return a dict which contain:
    - Method: str
    - Page: str
    - Headers: dict
    - Form: dict `If client send any form else None`
    - Param: dict `If client request any dynamic url. only work with PjonoApp`
    """
    json = {
    "Method": None,
    "Page": None,
    "Http": None,
    "Headers": {},
    "Form": {},
    "Param": {}
    }
    request = http_request.splitlines()
    try:
        r = request[0].split(" ")
    except IndexError:
        pass
    else:
        json["Method"] = r[0]
        json["Http"] = r[2]
        if "?" in r[1]:
            res = parse_dynamic_url(r[1])
            json["Page"] = res["Origin"]
            json["Param"] = res["Param"]
        else:
            json["Page"] = r[1]
        for line in request[1:]:
            if not line:
                continue
            if ":" in line:
                r = line.split(": ", 1)
                json["Headers"][r[0]] = r[1]
            elif "=" in line:
                r = line.split("=", 1)
                json["Form"][r[0]] = parse_http_encoding(r[1])
        return json

def parse_br(text: str):
    """
    parse_br will replace \\n with br
    """
    return text.replace("\n", "<br>")

def parse_dynamic_url(url: str):
    """
    Parsing dynamic url. Dynamic url is url with parameters.
    
    Example:
    - `example.com/search?q=python`
    - `example.com/find_user?username=John&id=880029`
    
    Return a dict which contain:
    - Origin: str `example: the origin of "/search?q=python" is "/search"`
    - Param: dict  `example: the param of "/user?name=John&id=7860" is {"name":"John", "id":"7860"}`
    
    Will return `None` if the url given isn't dynamic url
    """
    url1 = url.split("/")
    last_index = len(url1) - 1
    url2 = url1[last_index]
    if "?" not in url2:
        return None
    result = {
        "Origin": url.split("?")[0],
        "Param": {}
        }
    url2 = url2.split("?")[1]
    try:
        for param in url2.split("&"):
            pa = param.split("=")
            result["Param"][pa[0]] = parse_http_encoding(pa[1])
    except IndexError:
        pass
    return result

def parse_http_encoding(text: str):
    res = text
    res = res.replace("+", " ")
    for k, v in __ascii__.items():
        res = res.replace(k, v)
    return res