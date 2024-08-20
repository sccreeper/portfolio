import urllib.parse
import markdown
from markdown.extensions import Extension
from markdown.blockprocessors import BlockProcessor
import xml.etree.ElementTree as etree
import re
from dataclasses import dataclass
from src.mdextensions.image_processing_extension import process_image
import urllib

@dataclass
class Slide:
    src: str
    caption: str

# Made use of https://python-markdown.github.io/extensions/api/
class SlideshowBlockProcessor(BlockProcessor):
    # I hate regex.
    RE_FENCE_START = r'^\/{4}'
    RE_FENCE_END = r'\/{4}$'

    def test(self, parent, block):
        return re.match(self.RE_FENCE_START, block)

    def parse_slides(self, blocks: list[str]) -> list[Slide]:

        slides = []

        for b in blocks:
            if b == "" or b == "\n":
                continue
            else:

                data = b.split(" ", 1)

                src = "/content/" + process_image(data[0])
                src = urllib.parse.quote(src, safe="/")

                slides.append(Slide(src, data[1]))

        return slides

    def run(self, parent, blocks):

        original_block = blocks[0]
        blocks[0] = re.sub(self.RE_FENCE_START, '', blocks[0])

        for i, block in enumerate(blocks):
            if re.search(self.RE_FENCE_END, block):

                # Remove fence
                blocks[i] = re.sub(self.RE_FENCE_END, '', block)

                # Create slideshow parent element

                s: list[Slide] = self.parse_slides(blocks[0:i+1])

                slideshow = etree.SubElement(parent, "slide-show")

                for j, slide in enumerate(s):
                    slideshow.insert(j, etree.Element("slide", slide.__dict__))

                # Remove URL and caption blocks
                for j in range(0, i+1):
                    blocks.pop(0)

                return True
            
        blocks[0] = original_block
        return False
    
class SlideshowExtension(Extension):
    def extendMarkdown(self, md: markdown.Markdown):
        md.parser.blockprocessors.register(SlideshowBlockProcessor(md.parser), 'slideshow', 200)