from flask import request, url_for
import logging
import pickle
import os
import sqlite3 as sql
from flask_limiter import Limiter
from flask_compress import Compress

from src.constants import APPS_DATA_PATH, DATABASE_PATH, DATABASE_SCHEMA
from src._dataclasses import PostData
from src.shared import posts, htmx
from src.util import get_real_ip

from src.shared import app
app.config["SECRET_KEY"] = os.environ["SECRET"]

@app.context_processor
def inject_cf_keys():
    return dict(cfsitekey=os.environ["CF_TURNSTILE_SITE_KEY"])

@app.context_processor
def inject_canonical_url():
    can_url = url_for(request.endpoint, **request.view_args) if request.endpoint else ''
    return dict(can_url=can_url)


if os.environ["DEBUG"] == "true":
    app.logger.setLevel(logging.DEBUG)
else:
    app.logger.setLevel(logging.INFO)

limiter = Limiter(
    get_real_ip,
    app=app,
    default_limits=[f"{os.environ["RATE_LIMIT"]} per second"],
    storage_uri="memory://"
)

htmx.init_app(app)
compress = Compress()
compress.init_app(app)

con: sql.Connection = None
cur: sql.Cursor = None

# Remove whitespace in jinja

app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

# Init database

if not os.path.exists(DATABASE_PATH):
    con = sql.connect(DATABASE_PATH)
    con.execute(DATABASE_SCHEMA)
    con.close()

# Register sub-apps

print("Registering apps...")

if not os.path.exists(APPS_DATA_PATH):
    os.mkdir(APPS_DATA_PATH)

from src.apps.random_image import random_image

app.register_blueprint(random_image.random_image_app)

from src.comments import comment_blueprint

app.register_blueprint(comment_blueprint)
limiter.limit("60/minute" if os.environ["DEBUG"] == "true" else "30/minute")(comment_blueprint)

# Load pickled posts

for pickle_jar in os.listdir("content/"):
    if os.path.splitext(pickle_jar)[1] == ".pkl":
        with open(f"content/{pickle_jar}", "rb") as f:
            p: PostData = pickle.load(f)
            posts[p.meta.slug] = p

# Add any new posts to database

con = sql.connect(DATABASE_PATH)
cur = con.cursor()

for url in posts:

    cur.execute("SELECT * FROM posts WHERE slug = (?)", (url,))
    
    if cur.fetchone() == None:
        cur.execute("INSERT INTO posts (slug, views) VALUES (?, ?)", (url, 0))
        con.commit()
    else:
        continue

con.close()

# Sort posts

posts = {k: v for k, v in sorted(posts.items(), key=lambda item: item[1].meta.published.timestamp, reverse=True)}

print(f"Found and loaded {len(posts)} post(s)")

# Import routes
from src.handlers import *

if __name__ == "__main__":
    if os.environ["DEBUG"] == "true":
        app.logger.debug(f"Environment variables: {os.environ}")

        app.run(host="0.0.0.0",port=8000, debug=True)
    else:
        app.run(host="0.0.0.0",port=8000)