import markdown
from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor
import xml.etree.ElementTree as etree

PROTOCOL_SEC = "https://"
PROTOCOL = "http://"

class AnchorProcessor(Treeprocessor):
    
    def run(self, root):

        for i in range(len(root)):
            for anchor in root[i].iter("a"):
                if anchor.attrib["href"].startswith((PROTOCOL_SEC, PROTOCOL)):
                    anchor.attrib["target"] = "_blank"
                else:
                    anchor.attrib = {
                        "href" : anchor.attrib["href"],
                        "hx-trigger" : "click",
                        "hx-get" : anchor.attrib["href"],
                        "hx-push-url" : "true",
                        "hx-target" : "#content-block",
                        "hx-replace" : "innerHTML"
                    }

class AnchorTargetExtension(Extension):
    def extendMarkdown(self, md: markdown.Markdown) -> None:
        md.treeprocessors.register(AnchorProcessor(md), "anchortarget", 15)