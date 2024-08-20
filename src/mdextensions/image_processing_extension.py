import urllib.parse
import markdown
from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor
import os
import subprocess
import urllib
import xml.etree.ElementTree as etree

# Converts an image to AVIF and returns it's path

image_processing_exclusions = [".gif"]
processed_images = []

# JPEGs for actual pictures, PNGs for graphs/screenshots etc.

QUALITY_VALUES = {
    ".jpg" : "20%",
    ".png" : "50%"
}

def process_image(img_src: str) -> str:

    img_src = img_src.replace("/content/", "")
    img_src = urllib.parse.unquote(img_src) 

    if not os.path.exists(img_src):    
        if not img_src in processed_images:
            print(f"{img_src} doesn't exist")
            print(processed_images)

            return img_src

    
    filepath, ext = os.path.splitext(img_src)
    
    if ext in image_processing_exclusions:
        processed_images.append(img_src)
        return img_src
    elif img_src in processed_images:
        print(f"Already processed '{img_src}'")

        return f"{filepath}.avif"
    else:
        print(f"Processing '{img_src}'")

        subprocess.call(["magick", "convert", img_src, "-quality", QUALITY_VALUES[ext], filepath + ".avif"])
        os.remove(img_src)
        
        processed_images.append(img_src)
        return filepath + ".avif"
    
# Handles all extra processing that has to be done for images.

class ImageProcessor(Treeprocessor):
    
    def run(self, root):

        for i in range(len(root)):
            for _img in root[i].iter("img"):

                img_attrib = _img.attrib

                if "src" not in _img.attrib:
                    continue

                src = "/content/" + process_image(img_attrib["src"])
                src = urllib.parse.quote(src, safe="/")
                print(src)

                img_el = etree.Element("img")
                source_el = etree.Element("source", attrib={"srcset": src})

                _img.tag = "picture"
                _img.attrib = {}
                _img.append(source_el)
                _img.append(img_el)

                if "title" in img_attrib:
                    el = etree.Element("figcaption")
                    el.text = img_attrib["title"]
                    root.insert(i+1, el)

class ImageProcessorExtension(Extension):
    def extendMarkdown(self, md: markdown.Markdown) -> None:
        md.treeprocessors.register(ImageProcessor(md), "imageprocessor", 1)