
class HTML():
    """
    For opening and edit html
    """
    def __init__(self, html_file: str, pro: dict=None):
        self.content = open(html_file, "r", encoding="utf-8").read()
        if pro:
            for i, v in pro.items():
                self.content = self.content.replace(i, v)