from src.feeds.feed import *

feed_registry: dict[str, FeedInterface] = {}

# Add all feed types to registry

from src.feeds._rss import RSSFeed
from src.feeds._json import JSONFeed
from src.feeds._atom import AtomFeed

feed_registry[RSSFeed.type] = RSSFeed
feed_registry[JSONFeed.type] = JSONFeed
feed_registry[AtomFeed.type] = AtomFeed