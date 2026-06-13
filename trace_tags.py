import html.parser

class HTMLTracer(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = []
        self.void_elements = {
            'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
            'link', 'meta', 'param', 'source', 'track', 'wbr'
        }

    def handle_starttag(self, tag, attrs):
        if tag in self.void_elements:
            return
        # Get id or class if present
        el_id = next((val for name, val in attrs if name == 'id'), None)
        el_class = next((val for name, val in attrs if name == 'class'), None)
        desc = f"{tag}"
        if el_id:
            desc += f"#{el_id}"
        elif el_class:
            desc += f".{el_class.split()[0]}"
            
        self.stack.append(desc)
        path = " > ".join(self.stack)
        print(f"L{self.getpos()[0]}: Open {path}")

    def handle_endtag(self, tag):
        if tag in self.void_elements:
            return
        if self.stack:
            path = " > ".join(self.stack)
            print(f"L{self.getpos()[0]}: Close {path}")
            self.stack.pop()

tracer = HTMLTracer()
with open('frontend/index.html', 'r', encoding='utf-8') as f:
    tracer.feed(f.read())
