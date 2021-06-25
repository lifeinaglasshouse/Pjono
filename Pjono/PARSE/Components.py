from typing import Callable
from Pjono.PARSE.Html import HTML
from bs4 import BeautifulSoup, Tag

class Component:
    """
    Component class
    
    - `tag_name: str`
    
        Tag name
    
    - `datas=None`
    
        Tag content
        
    - `End_tag: bool=True`
    
        If tag does have end tag
        
    - `**attr`
    
        Tag attributes
        
    Class Attributes:
    
    - `self.tag: str`
    - `self.datas: list | None`
    - `self.attr: dict`
    - `self.end: bool`
    """
    def __init__(self, tag_name: str, datas=None, End_tag: bool=True, **attr):
        self.tag = tag_name.split(" ")[0]
        self.datas = datas if isinstance(datas, list) else [str(datas)] if End_tag else None
        self.attr = attr
        self.end = End_tag

    def __repr__(self) -> str:
        attr = " ".join([f'{k}="{v if isinstance(v, str) else " ".join(v)}"' for k, v in self.attr.items()])
        value = self.datas if not isinstance(self.datas, list) else "".join([str(i) for i in self.datas])
        return f"<{self.tag}{' ' + attr if attr else ''}>{value}</{self.tag}>" if self.end else f"<{self.tag}{' ' + attr if attr else ''}>"
    
    def __eq__(self, o: object) -> bool:
        return self.__class__ == o.__class__ and self.__dict__ == o.__dict__
    
    def __getitem__(self, index: int):
        return self.datas[index]
    
    @classmethod
    def DictToComponent(cls, tag_dict: dict):
        """
        Convert dict to component. The dict must have:
        
        - Name: str
        - Data: list | str | None
        - EndTag: bool
        - Attrs: dict
        """
        if isinstance(tag_dict["Data"], list):
            datas = [Component.DictToComponent(data) if isinstance(data, dict) else data for data in tag_dict["Data"]]
        else:
            datas = tag_dict["Data"]
        return cls(tag_dict["Name"], datas, tag_dict["EndTag"], **tag_dict["Attrs"])
    
    @classmethod 
    def StrToComponent(cls, tag: str):
        """
        Convert string to component. Example:
        `"<h1>Hello, World!</h1>"` = `<Component:Name="h1";Datas="Hello, World!";End=True;Attrs={}>`
        """
        return Component.DictToComponent(_tag_dict(BeautifulSoup(tag, "html.parser").find_all()[0]))

def _tag_dict(tag: Tag):
    end = True if str(tag).endswith(f"</{tag.name}>") else False
    result = {
        "Name": tag.name,
        "Attrs": tag.attrs,
        "Data": [],
        "EndTag": end
    }
    if tag.contents:
        for content in tag.contents:
            if content == "\n":
                continue
            result["Data"].append(_tag_dict(content) if isinstance(content, Tag) else str(content))
    return result

class HtComponents:
    """
    HtComponents class
    
    Used for building user interface with Component.
    ```py
    @app.register("/")
    def index(request):
        hc = HtComponents(f\"""
        <div>
        <form action="/" method="GET">
            <input name="num1" type="number">
            <p>+</p>
            <input name="num2" type="number"><br><br>
            <input type="submit" value="Answer">
        </form>
        </div>
        \""")
        if "num1" in request["Param"] and "num2" in request["Param"]:
            hc.append(lambda c: c.tag == "div", Component("h1", request["Param"]["num1"]+request["Param"]["num2"]))
        return hc.render(HTML("test.html"), id="root")
    ```
    """
    def __init__(self, html: str):
        self.components = Component.DictToComponent(_tag_dict(BeautifulSoup(html, "html.parser").find_all()[0]))

    def __repr__(self):
        return str(self.components)
    
    def render(self, HTML_obj: HTML, id: str):
        """
        Render Components into tag with passed id in HTML content
        """
        hc = HtComponents(HTML_obj.content)
        hc.replace_value(lambda c: "id" in c.attr and c.attr["id"] == id, self.components)
        return str(hc)

    def replace_value(self, _func: Callable, value):
        """
        Replace Component value.\n`_func` is for filtering Component: `lambda c: c.tag == "h1"`
        """
        result = []
        if _func(self.components):
            self.components.datas = value if isinstance(value, Component) else value[0]
            return
        for c in self.components.datas:
            if isinstance(c, Component):
                if _func(c):
                    c.datas = value if isinstance(value, list) else [value]
                    result.append(c)
                else:
                    if c.datas and c.end:
                        h = HtComponents(str(c))
                        h.replace_value(_func, value)
                        result.append(h)
                    else:
                        result.append(c)
        if result:
            self.components.datas = result
            
    def append(self, _func: Callable, _object):
        """
        Append object.\n`_func` is for filtering Component: `lambda c: c.tag == "h1"`
        """
        result = []
        if _func(self.components):
            self.components.datas.append(_object)
            return
        for c in self.components.datas:
            if isinstance(c, Component):
                if _func(c):
                    c.datas.append(_object)
                    result.append(c)
                else:
                    if c.datas and c.end:
                        h = HtComponents(str(c))
                        h.append(_func, _object)
                        result.append(h)
                    else:
                        result.append(c)
        if result:
            self.components.datas = result