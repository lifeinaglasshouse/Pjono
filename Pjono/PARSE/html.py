
class HTML():
    
    def __init__(self, html_file: str, property: dict=None):
        self.content = open(html_file, "r", encoding="utf-8").read()
        if property:
            for i, v in property.items():
                self.content = self.content.replace(i, v)