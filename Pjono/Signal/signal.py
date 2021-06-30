from Pjono.Response import Http_File
from Pjono.Server import PjonoApp
import os

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

def _get_path(path: set):
    return os.path.join(__location__, path)

class ClientEvent:
    """
    Class for adding and getting event
    ```py
    app = PjonoApp()
    client = ClientEvent(app)    
    ```
    """
    def __init__(self, server: PjonoApp):
        self.app = server
        self.app.add_file("/Pjono/signal.js", Http_File(_get_path("signal.js"), "application/javascript"))
        self.events = {}
    
    def addEvent(self, name: str):
        """
        decorator function for adding new event or overwriting existed event
        ```py
        @client.addEvent("yell")
        def yell(msg):
            return msg.upper()+"!!!"
            
        @app.register("/")
        def index(request):
            signal, event = client.getEvent(request)
            if signal and event == "yell":
                return signal
            return HTML("index.html")
        ```
        to fire the event, we used signal.js:
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
                <button onclick="yell()">yell</button>
            </div>
            <script>
            const Signal = new PjSignal();
            function yell(){
                Signal.fireEvent("yell", document.getElementById("inp-1").value, function(response, status){
                    var ele = document.createElement("h2");
                    ele.textContent = response;
                    document.getElementById("root").appendChild(ele);
                });
            }
            </script>
        </body>
        ```
        """
        def inner(_func):
            self.events[name] = _func
        return inner
    
    def getEvent(self, request: dict):
        """
        Getting event with message.
        Will return None if there's no event happen
        ```py
        @app.register("/")
        def index(request):
            signal, event = client.getEvent(request)
            if signal and event == "onclick":
                return signal
            return HTML("index.html")
        ```
        """
        if "PjEvent" in request["Headers"] and "Pjmsg" in request["Headers"]:
            event = request["Headers"]["PjEvent"]
            msg = request["Headers"]["Pjmsg"]
            if event in self.events:
                return self.events[event](msg), event
        return None, None
    
class SignalCode:
    """
    SignalCode
    
    Telling the server about current event status.
    ### Example:
    ```py
    @client.addEvent("user_id")
    def get_user_id(id):
        if id in user:
            return user[id]["name"]
        return SignalCode("Not Found", 404)

    @app.register("/")
    def index(request):
        signal, event = client.getEvent(request)
        if signal and event == "user_id":
            if signal == 404:
                return "User Not Found"
            return signal
        return HTML("html/index.html")
    ```
    """
    def __init__(self, name: str, code: int):
        self.code = code
        self.name = name
        
    def __repr__(self) -> str:
        return f"<{self.name}:{self.code}>"
    
    def __eq__(self, o: int) -> bool:
        return self.code == o