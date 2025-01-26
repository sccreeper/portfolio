import markdown
from markdown.inlinepatterns import InlineProcessor
from markdown.extensions import Extension
import xml.etree.ElementTree as etree
import re

# The following regexes match strings in the form:
# @green This text should be green @
# @#ff00ff This text should be purple @
# @#fff This text should be white @

REGEX_START = r'\@(?:[a-zA-Z]+|#[0-9a-fA-F]{3,6})\s+'
REGEX_END = r'\s+\@'
REGEX_COMPLETE = r'\@([a-zA-Z]+|#[0-9a-fA-F]{3,6})\s+(.*?)\s+\@'

class ColourPattern(InlineProcessor):
    def handleMatch(self, m, data):
        
        el = etree.Element("span")
        el.attrib["style"] = f"color: {m.group(1)};"
        el.text = m.group(2)
        return el, m.start(0), m.end(0)
    
    def getCompiledRegExp(self):
        return re.compile(REGEX_COMPLETE)

class ColourExtension(Extension):
    def extendMarkdown(self, md: markdown.Markdown) -> None:
        md.inlinePatterns.register(ColourPattern(REGEX_COMPLETE, md), "colourprocessor", 50)