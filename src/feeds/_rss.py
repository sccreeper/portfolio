from src import PostMeta
from xml.etree import ElementTree as ET
from src.feeds import FeedInterface, DEFAULT_TITLE, DEFAULT_DESCRIPTION, DEFAULT_URL
import datetime
from email.utils import format_datetime

POST_LIMIT: int = 5

DEFAULT_ROOT: ET.Element = ET.Element("rss", attrib={"version": "2.0",  "xmlns:atom":"http://www.w3.org/2005/Atom"})
DEFAULT_CHANNEL: ET.Element = ET.SubElement(DEFAULT_ROOT, "channel")

# Add sub elements that don't need to be referenced later

#Required
_TITLE_EL = ET.SubElement(DEFAULT_CHANNEL, "title")
_TITLE_EL.text = DEFAULT_TITLE
_DESCRIPTION_EL = ET.SubElement(DEFAULT_CHANNEL, "description")
_DESCRIPTION_EL.text = DEFAULT_DESCRIPTION
_LINK_EL = ET.SubElement(DEFAULT_CHANNEL, "link")
_LINK_EL.text = DEFAULT_URL

# Optional

_LANGUAGE_EL = ET.SubElement(DEFAULT_CHANNEL, "language")
_LANGUAGE_EL.text = "en-gb"
_GENERATOR_EL = ET.SubElement(DEFAULT_CHANNEL, "generator")
_GENERATOR_EL.text = "Oscar Peace's Blog Engine"

ET.SubElement(DEFAULT_CHANNEL, "atom:link", attrib={"href" : "https://www.oscarcp.net/feeds/rss", "rel":"self", "type":"application/rss+xml"})

def _post_to_element(post: PostMeta) -> ET.Element:

    root = ET.Element("item")
    
    title = ET.SubElement(root, "title")
    title.text = post.title
    link = ET.SubElement(root, "link")
    link.text = f"https://www.oscarcp.net/blog/{post.slug}"
    
    desc = ET.SubElement(root, "description")
    desc.text = post.summary

    pub_date = ET.SubElement(root, "pubDate")
    pub_date.text = format_datetime(datetime.datetime.fromtimestamp(post.published.timestamp))
    guid = ET.SubElement(root, "guid")
    guid.text = f"https://www.oscarcp.net/blog/{post.slug}"

    return root

class RSSFeed(FeedInterface):
    type = "rss"
    extension = ".xml"
    file = "rss.xml"

    def generate_feed(_posts: list[PostMeta]) -> bytes:
        root_copy = DEFAULT_ROOT
        channel = root_copy.find("channel")

        for post in _posts:
            channel.append(_post_to_element(post))

        return ET.tostring(root_copy)

