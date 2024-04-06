import markdown
from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor
import xml.etree.ElementTree as etree

class ImageCaptionProcessor(Treeprocessor):

    def run(self, root):

        for i in range(len(root)):
            for img in root[i].iter("img"):
                if "title" in img.attrib:
                    el = etree.Element("figcaption")
                    el.text = img.attrib["title"]
                    root.insert(i+1, el)

class ImageCaptionExtension(Extension):
    def extendMarkdown(self, md: markdown.Markdown) -> None:
        md.treeprocessors.register(ImageCaptionProcessor(md), "imagecaption", 10)
                