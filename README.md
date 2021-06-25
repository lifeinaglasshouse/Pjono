# Pjono
## Web Framework for Python

****

## About the project:

a framework for making a webserver. You can also use it to build
user interface with `Components.py`

**Built with:**
- Socket

## Usage:
```py
from Pjono import PjonoApp, Http_Response, Http_File, HTML

app = PjonoApp()

app.add_file("/style.css", Http_File("style.css", "text/css"))

@app.register("/")
def index(request):
    return Http_Response(content=HTML("index.html"))

app.launch()
```
You can also use it to parse http request
```py
from Pjono.PARSE import parse_request

request = """\
GET /index.html HTTP/1.1
User-Agent: Mozilla/4.0 (compatible; MSIE5.01; Windows NT)
Host: www.example.com
Accept-Language: en-us
Accept-Encoding: gzip, deflate
Connection: Keep-Alive"""

print(parse_request(request))
```

## Contributing
1. Fork the project
2. Create your Feature Branch: `git checkout -b feature/{feature}`
3. Commit your Changes: `git commit -m 'Add some AmazingFeature'`
4. Push to the Branch: `git push origin feature/AmazingFeature`
5. Open a Pull Request

## License

Distributed under the **MIT License**. See `LICENSE` for more information

## Quick Link

- [Official Website](https://pjono.tk)
- [Github](https://github.com/Xp-op/Pjono)