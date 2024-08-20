from dataclasses import dataclass
from flask_limiter import Limiter
from flask_htmx import HTMX
from flask import Flask

APPS_DATA_PATH: str = "/var/lib/portfolio/apps"

@dataclass(order=True)
class PostMeta():
    title: str
    summary: str
    authour: str
    tags: list[str]
    published: str
    slug: str

    timestamp: int
    length: int

@dataclass
class PostData:
    meta: PostMeta
    body: str

posts: dict[str, PostData] = {}

limiter: Limiter = None
htmx: HTMX = HTMX()
app: Flask = Flask(__name__)