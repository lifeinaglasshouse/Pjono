# Pjono
## Web Framework for Python

****

## About the project:

There are many Python web frameworks and some of them are better than Pjono. The reasons I made Pjono is because:

- To understanding how Http work
- Learn about Python much deeper

**This is the Pjono first version, not recommend to use in big project because of bugs**

**Built with:**
- Socket

## Usage:
```py
from Pjono import PjonoApp, Http_Response, Http_File, HTML

app = PjonoApp()

app.add_file("/style.css", Http_File("style.css", "text/css"))

@app.register("/")
def index(request):
    return Http_Response(response_headers={
        "CONTENT": HTML("index.html").content
    })

app.launch()
```
You can also use it to parse http request
```py
from Pjono.PARSE.parse import parse_request

request = """\
GET /index.html HTTP/1.1
User-Agent: Mozilla/4.0 (compatible; MSIE5.01; Windows NT)
Host: www.example.com
Accept-Language: en-us
Accept-Encoding: gzip, deflate
Connection: Keep-Alive"""

print(parse_request(request))
```

## Documentation
You can find the docs [here](https://pjono.tk)

## Contributing
1. Fork the project
2. Create your Feature Branch: `git checkout -b feature/{feature}`
3. Commit your Changes: `git commit -m 'Add some AmazingFeature'`
4. Push to the Branch: `git push origin feature/AmazingFeature`
5. Open a Pull Request

## License

Distributed under the **MIT License**. See `LICENSE` for more information
