from src._dataclasses import PostData

DEFAULT_TITLE = "Oscar Peace's blog"
DEFAULT_DESCRIPTION = "Feed for the blog at www.oscarcp.net"
DEFAULT_URL = "https://www.oscarcp.net"

class FeedInterface:
    type: str
    extension: str
    file: str

    def generate_feed(posts: list[PostData]) -> bytes:
        """Generates a feed given a list of posts"""
        pass