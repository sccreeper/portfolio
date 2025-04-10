from src._dataclasses import PostData
from src.feeds import FeedInterface, DEFAULT_TITLE, DEFAULT_DESCRIPTION, DEFAULT_URL
import datetime
import json

_FEED_TEMPLATE = {
    "version": "https://jsonfeed.org/version/1.1",
    "title": DEFAULT_TITLE,
    "home_page_url": DEFAULT_URL,
    "feed_url": "https://www.oscarcp.net/feeds/json",
    "description": DEFAULT_DESCRIPTION
}

class JSONFeed(FeedInterface):
    file = "feed.json"
    extension = ".json"
    type = "json"

    def generate_feed(_posts: list[PostData]) -> bytes:
        feed_template_copy = _FEED_TEMPLATE

        feed_template_copy["items"] = []

        for post in _posts:
            feed_template_copy["items"].append(
                {
                    "id": f"https://www.oscarcp.net/blog/{post.meta.slug}",
                    "url": f"https://www.oscarcp.net/blog/{post.meta.slug}",
                    "summary": post.meta.summary,
                    "title": post.meta.title,
                    "content_text": post.body,
                    "date_published": datetime.datetime.fromtimestamp(post.meta.published.timestamp).isoformat()
                }
            )

        return str.encode(json.dumps(feed_template_copy))
        