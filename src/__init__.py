from dataclasses import dataclass
from flask_limiter import Limiter
from flask_htmx import HTMX

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

# TODO: Combine these - 18/07/24
posts: list[Post] = []
post_slugs: list[str] = []

limiter: Limiter = None
htmx: HTMX = HTMX()