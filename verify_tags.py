import html.parser

class HTMLTagChecker(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = []
        self.errors = []
        # List of tags that are self-closing (void elements) in HTML5
        self.void_elements = {
            'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
            'link', 'meta', 'param', 'source', 'track', 'wbr'
        }

    def handle_starttag(self, tag, attrs):
        if tag in self.void_elements:
            return
        self.stack.append((tag, self.getpos()))

    def handle_endtag(self, tag):
        if tag in self.void_elements:
            return
        if not self.stack:
            self.errors.append(f"Unexpected end tag </{tag}> at line {self.getpos()[0]}, col {self.getpos()[1]}")
            return
        
        expected_tag, pos = self.stack.pop()
        if expected_tag != tag:
            # Check if this tag is in the stack to see if we missed a closing tag
            found = False
            for idx, (t, p) in enumerate(reversed(self.stack)):
                if t == tag:
                    found = True
                    skip_count = idx + 1
                    break
            
            if found:
                self.errors.append(f"Mismatched end tag </{tag}> at line {self.getpos()[0]}, col {self.getpos()[1]} (expected </{expected_tag}> from line {pos[0]}, col {pos[1]}). Implicitly closing tags: {[t for t, p in self.stack[-skip_count:]]}")
                # Pop the skipped tags
                for _ in range(skip_count):
                    self.stack.pop()
            else:
                self.errors.append(f"Unexpected end tag </{tag}> at line {self.getpos()[0]}, col {self.getpos()[1]} (expected </{expected_tag}> from line {pos[0]}, col {pos[1]})")

    def check(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            self.feed(f.read())
        
        while self.stack:
            tag, pos = self.stack.pop()
            self.errors.append(f"Unclosed tag <{tag}> at line {pos[0]}, col {pos[1]}")
            
        return self.errors

checker = HTMLTagChecker()
errors = checker.check('frontend/index.html')
if errors:
    print("Found HTML structure errors:")
    for err in errors:
        print("  -", err)
else:
    print("HTML structure is perfectly valid!")
