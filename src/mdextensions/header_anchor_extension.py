import markdown
from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor
from xml.etree import ElementTree as etree

ALPHABET = "abcdefghijklmnopqrstuvwxyz123456790"
HEADER_LEVELS = {
    "h1" : 1,
    "h2" : 2,
    "h3" : 3,
}

class HeaderProcessor(Treeprocessor):
    
    def run(self, root):

        for i in range(len(root)):
            # Loop through the multiple header lists combined
            for header in [*root[i].iter("h1"), *root[i].iter("h2"), *root[i].iter("h3")]:

                anchor_id = ""

                for char in header.text:
                    if char.lower() in ALPHABET:
                        anchor_id += char.lower()
                    elif char == " ":
                        anchor_id += "-"
                    else: continue

                anchor = etree.Element("a", attrib={"href": f"#{anchor_id}"})
                anchor.text = "#" * HEADER_LEVELS[header.tag]

                header_new = etree.Element(header.tag)
                header_new.text = header.text
                
                header.tag = "span"
                header.attrib["id"] = anchor_id
                header.attrib["class"] = "header"
                header.text = ""
                
                header.append(anchor)
                header.append(header_new)

class HeaderAnchorExtension(Extension):
    def extendMarkdown(self, md: markdown.Markdown) -> None:
        md.treeprocessors.register(HeaderProcessor(md), "headeranchor", 15)