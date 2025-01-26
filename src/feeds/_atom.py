from src._dataclasses import PostData
from src.feeds import DEFAULT_DESCRIPTION, DEFAULT_TITLE, DEFAULT_URL, FeedInterface
from datetime import datetime
import html

from xml.etree import ElementTree as ET

# Base feed

_ROOT = ET.Element("feed", attrib={"xmlns":"http://www.w3.org/2005/Atom"})
_TITLE = ET.SubElement(_ROOT, "title")
_TITLE.text = DEFAULT_TITLE
ET.SubElement(_ROOT, "link", attrib={"href":DEFAULT_URL})
_UPDATED = ET.SubElement(_ROOT, "updated")
_UPDATED.text = datetime.now().isoformat()
_SUBTITLE = ET.SubElement(_ROOT, "subtitle")
_SUBTITLE.text = DEFAULT_DESCRIPTION
_ID = ET.SubElement(_ROOT, "id")
_ID.text = html.escape(DEFAULT_URL) + "/"

ET.SubElement(_ROOT, "link", attrib={"href" : "https://www.oscarcp.net/feeds/atom", "rel":"self", "type":"application/atom+xml"})

def _post_to_element(post: PostData) -> ET.Element:
    root = ET.Element("entry")
    title = ET.SubElement(root, "title")
    title.text = post.meta.title
    ET.SubElement(root, "link", attrib={"href":"https://www.oscarcp.net/"})
    _id = ET.SubElement(root, "id")
    _id.text = f"https://www.oscarcp.net/blog/{post.meta.slug}"
    updated = ET.SubElement(root, "updated")
    updated.text = datetime.fromtimestamp(post.meta.published.timestamp).isoformat()
    summary = ET.SubElement(root, "summary")
    summary.text = post.meta.summary
    content = ET.SubElement(root, "content", {"type":"xhtml"})
    content_div = ET.SubElement(content, "div", {"xmlns":"http://www.w3.org/1999/xhtml"})
    content_div.text = post.body

    authour = ET.SubElement(root, "author")
    name = ET.SubElement(authour, "name")
    name.text = "Oscar Peace"

    return root
    

class AtomFeed(FeedInterface):
    type = "atom"
    extension = ".xml"
    file = "atom.xml"

    def generate_feed(_posts: list[PostData]) -> bytes:
        root_copy = _ROOT

        for post in _posts:
            root_copy.append(_post_to_element(post))

        return ET.tostring(root_copy)