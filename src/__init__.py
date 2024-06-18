from dataclasses import dataclass
from xml.etree import ElementTree as ET
from datetime import datetime
from email.utils import format_datetime

APPS_DATA_PATH: str = "/var/lib/portfolio/apps"

@dataclass(order=True)
class Post():
    title: str
    summary: str
    authour: str
    tags: list[str]
    published: str
    url: str

    timestamp: int
    length: int

    def to_element(self, slug: str) -> ET.Element:

        root = ET.Element("item")
        
        title = ET.SubElement(root, "title")
        title.text = self.title
        link = ET.SubElement(root, "link")
        link.text = f"https://www.oscarcp.net/blog/{slug}"
        
        desc = ET.SubElement(root, "description")
        desc.text = self.summary
        # authour = ET.SubElement(root, "author")
        # authour.text = self.authour

        pub_date = ET.SubElement(root, "pubDate")
        pub_date.text = format_datetime(datetime.fromtimestamp(self.timestamp))
        guid = ET.SubElement(root, "guid")
        guid.text = f"https://www.oscarcp.net/blog/{slug}"

        return root

# TODO: Combine these - 18/07/24
posts: list[Post] = []
post_slugs: list[str] = []