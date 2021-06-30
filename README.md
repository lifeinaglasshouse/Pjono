<div align="center">
    <img src="https://i.ibb.co/d471Cfp/pjono.png" width="240" height="240" alt="icon">
    <br>
    <img src="https://img.shields.io/static/v1?label=version&message=0.0.4&color=blue&style=for-the-badge" alt="version">
    <img src="https://img.shields.io/static/v1?label=star&message=2&color=yellow&style=for-the-badge" alt="star">
    <img src="https://img.shields.io/static/v1?label=contributors&message=1&color=green&style=for-the-badge" alt="contributors">
    <img src="https://img.shields.io/static/v1?label=Forks&message=0&color=light-blue&style=for-the-badge" alt="Fork">
    <img src="https://img.shields.io/static/v1?label=Issues&message=0&color=red&style=for-the-badge" alt="Issues">
    <h2>A Python Web Framework Built With Socket</h2>
    <h3>High Performance • Light Weight • Not really</h3>
    <br>
    <img src="https://opengraph.githubassets.com/6700eb351d4a7559a7b78dcd8b9ca2721157981b04fc98903c8783225f54591b/Xp-op/Pjono" width="500" style="border-radius: 20px">
    <br>
</div>

## About
Pjono is a framework for creating web server, api, and any other thing that it can do.

The reason I used Socket is that I really like Socket and it much easier to used.

Making the server receiving and sending data is easy but parsing Http Request and creating Http Response are quite a bit tricky since I don't have people that can help me. I also try to add new feature for building User Interface and I had to use Third Party Library(bs4) for parsing html code. This project made me understand how HTTP actually work. Really glad that I can finish this.

## Features
- Components

    Building User Interface with `Components.py` module.

    Example:
    ```py
    from Pjono import HtComponents, HTML

    HtComponents(f"""
    <div class="container-1">
        <h1>(2+2)/5={(2+2)/5}</h1>
        <h1>2*4-(9%2)={2*4-(9%2)}</h1>
        <h1>1 is 1={1 == 1}</h1>
        <h1>"Hello" is a string={isinstance("Hello", str)}</h1>
        <h1>{", ".join(str(i) for i in range(1,11))}</h1>
    </div>
    """).render(HTML("index.html"), id="root")
    ```

    You can also append object to specific element:
    ```py
    from Pjono import HtComponents, Component

    Parent = HtComponents("<div id='root'></div>")

    Parent.append(lambda c: "id" in c.attr and c.attr["id"] == "root", Component("h1","Hello, World!"))
    #<div id="root">
    #   <h1>Hello, World!</h1>
    #</div>
    ```
    Converting string or dict into Component object:
    ```py
    from Pjono import Component

    comp = Component.StrToComponent("<h2 class='title'>Inside the hole of hell</h2>")
    # Component("h2", "Inside the hole of hell", True, **{"class":"title"})

    comp = Component.DictToComponent({
        "Name": "div",
        "Data": "This is div class",
        "EndTag": True,
        "Attrs":{
            "id":"Container"
        }
    })
    # Component("div", "This is div class", True, id="Container")
    ```

- Signal and Event

    With this feature, you can execute any Python function on client side but you still need JS to make it work.

    How it Work? It simple.

    <div align="center">
    <img src="https://i.ibb.co/SfDRnvj/image.png" width="500" style="border-radius: 10px" alt="scenario">
    <br>
    </div>

    client will send a request to the server with JS and
    the server will get the event name and message by headers. Server will get the function that supposed to handle the request and execute it.

    ```py
    from Pjono import PjonoApp, ClientEvent, HTML

    # Creating PjonoApp and ClientEvent object
    app = PjonoApp("Example Server")
    client = ClientEvent(app)

    # Add new event
    @client.addEvent("upper")
    def upper(msg):
        return msg.upper()

    # Register new location
    @app.register("/")
    def index(request):
        signal, event = client.getEvent(request) # process the request
        if signal and event == "upper": # if the request is an event
            return signal # msg.upper()
        return HTML("index.html") # if not then send the index.html content
    ```

    and the JS part:

    ```html
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>index</title>
        <script src="/Pjono/signal.js"></script>
    </head>
    <body>
        <div id="root">
            <input name="msg" type="text" id="inp-1"><br><br>
            <button onclick="upper()">Upper</button>
        </div>
        <script>
        const Signal = new PjSignal();
        function upper(){
            Signal.fireEvent("upper", document.getElementById("inp-1").value, function(response, status){
                var ele = document.createElement("h2");
                ele.textContent = response;
                document.getElementById("root").appendChild(ele);
            });
        }
        </script>
    </body>
    ```

## Features that may be added

- WebSocket

    want to make chat app like Discord?

- Components.py Improvement

    More HtComponents features such as extend, insert, delete and more.

- File upload support

    This one is kinda hard to do but I'll try to make it

## Usage

for more information, read the [documentation](https://github.com/Xp-op/Pjono/wiki/Documention).
```py
from Pjono import PjonoApp

app = PjonoApp("My Server")

@app.register("/")
def index(request):
    return "<h1>Hello, World</h1>"

app.launch()
```

## License
Distributed under the MIT License. See `LICENSE` for more information.

## Contributing
Contributions can help make this project much better. All contributions are **greatly appreciated**.
1. Fork the project
2. Create your Feature Branch

    `git checkout -b feature/EpicFeature`

3. Commit your changes

    `git commit -m 'cool feature that can...'`

4. Push to the Branch

    `git push origin feature/EpicFeature`

5. Open a Pull Request

