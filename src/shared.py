from flask_limiter import Limiter
from flask_htmx import HTMX
from flask_caching import Cache
from flask import Flask

from src._dataclasses import PostData

limiter: Limiter = None
htmx: HTMX = HTMX()
app: Flask = Flask(__name__)
cache: Cache = Cache(config={"CACHE_TYPE": "SimpleCache"})
posts: dict[str, PostData] = {}