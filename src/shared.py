from flask_limiter import Limiter
from flask_htmx import HTMX
from flask import Flask

from src._dataclasses import PostData

limiter: Limiter = None
htmx: HTMX = HTMX()
app: Flask = Flask(__name__)
posts: dict[str, PostData] = {}