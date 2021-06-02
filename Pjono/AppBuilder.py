import sys
import os

arg = sys.argv

arg.pop(0)

if len(arg) < 1:
    print("Please enter your app name")
    quit()

os.makedirs(arg[0])
os.makedirs(arg[0] + "/html")
os.makedirs(arg[0] + "/css")
os.makedirs(arg[0] + "/js")

with open(f"{arg[0]}/main.py", "w") as fp:
    fp.write("""\
from Pjono import PjonoApp, Http_Response, HTML, Http_File

app = PjonoApp() # http://localhost:5500/

app.add_file("/css/style.css", Http_File("css/style.css", "text/css"))
app.add_file("/js/script.js", Http_File("css/style.css", "text/javascript"))

# Register new page called "index"
@app.register("/")
def index(request):
    # Return the Http Response
    return Http_Response(status_code=(200, "OK"), response_data={
        "CONTENT": HTML("html/index.html").content,
        "Content-Type": "text/html",
        "Connection": "Close"
    })

# Launch the server with debug true
app.launch(debug=True)
""")
    
with open(f"{arg[0]}/html/index.html", "w") as fp:
    fp.write(f"""\
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{arg[0]}</title>
    <link rel="stylesheet" href="/css/style.css">
</head>
<body>
    <div class="container">
        <h1 class="text" id="text">Hello World!</h1>
        <input type="text" id="usr_input" value="Hello World!" class="input"><br>
        <button class="btn" onclick="changeText()">Change Text</button>
    </div>
    <script src="/js/script.js"></script>
</body>
</html>""")
    
with open(f"{arg[0]}/css/style.css", "w") as fp:
    fp.write("""\

head, body{
    margin: 0;
    padding: 0;
}

.container{
    width: 100%;
}

.text{
    text-align: center;
    font-family: consolas;
    font-size: 40px;
}

.input{
    display: block;
    margin: 0px auto;
    font-size: 30px;
}

.btn{
    display: block;
    margin: 0px auto;
}
""")
    
with open(f"{arg[0]}/js/script.js", "w") as fp:
    fp.write("""\
function changeText(){
    var text = document.getElementById("text")
    var input = document.getElementById("usr_input")
    text.innerText = input.value
}
""")