from src import Post, post_slugs
from xml.etree import ElementTree as ET

POST_LIMIT: int = 5

DEFAULT_ROOT: ET.Element = ET.Element("rss", attrib={"version": "2.0"})
DEFAULT_CHANNEL: ET.Element = ET.SubElement(DEFAULT_ROOT, "channel")

# Add sub elements that don't need to be referenced later

#Required
_TITLE_EL = ET.SubElement(DEFAULT_CHANNEL, "title")
_TITLE_EL.text = "Oscar Peace's blog"
_DESCRIPTION_EL = ET.SubElement(DEFAULT_CHANNEL, "description")
_DESCRIPTION_EL.text = "RSS Feed for the blog at www.oscarcp.net"
_LINK_EL = ET.SubElement(DEFAULT_CHANNEL, "link")
_LINK_EL.text = "https://www.oscarcp.net"

# Optional

_LANGUAGE_EL = ET.SubElement(DEFAULT_CHANNEL, "language")
_LANGUAGE_EL.text = "en-gb"
_GENERATOR_EL = ET.SubElement(DEFAULT_CHANNEL, "generator")
_GENERATOR_EL.text = "Oscar Peace's Blog Engine"

def generate_rss_feed(_posts: list[Post]) -> bytes:

    root_copy = DEFAULT_ROOT
    channel = root_copy.find("channel")

    for i, post in enumerate(_posts):
        channel.insert(len(list(channel.iter()))-1, post.to_element(post_slugs[i]))

    return ET.tostring(root_copy)