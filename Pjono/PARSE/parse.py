"""
Example http_request:

GET /index.html HTTP/1.1
User-Agent: Mozilla/4.0 (compatible; MSIE5.01; Windows NT)
Host: www.example.com
Accept-Language: en-us
Accept-Encoding: gzip, deflate
Connection: Keep-Alive
"""

import os

def parse_request(http_request: str):
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
        json["Page"] = r[1]
        json["Http"] = r[2]
        request.pop(0)
        for line in request:
            if not line:
                continue
            if ":" in line:
                r = line.split(": ", 1)
                json["Headers"][r[0]] = r[1]
            elif "=" in line:
                r = line.split("=", 1)
                json["Form"][r[0]] = r[1]
        return json

def parse_br(text: str):
    result = []
    for line in text.splitlines():
        if not line:
            continue
        result.append(f"{line}<br>")
    result = "\n".join(result)
    return os.linesep.join([s for s in result.splitlines() if s])

def parse_dynamic_url(url: str):
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
            result["Param"][pa[0]] = pa[1]
    except IndexError:
        pass
    return result