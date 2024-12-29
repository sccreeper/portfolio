from flask import request, url_for
import logging
import pickle
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from flask_limiter import Limiter
from flask_compress import Compress

from src.constants import APPS_DATA_PATH, DATA_VERSION_PATH, DATABASE_PATH
from src._dataclasses import PostData
from src.shared import posts, htmx, cache, app
from src.util import get_real_ip
from src.db.models import PostModel
from src.db import db

app.config["SECRET_KEY"] = os.environ["SECRET"]
app.config["DEBUG"] = os.environ["DEBUG"] == "true"

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
    default_limits=[f"{os.environ["RATE_LIMIT"]} per second"],
    storage_uri="memory://"
)

compress = Compress()

compress.init_app(app)
htmx.init_app(app)
cache.init_app(app)
limiter.init_app(app)

if os.path.exists(DATA_VERSION_PATH):
    old_ver_number: int
    with open(DATA_VERSION_PATH, "r") as f:
        old_ver_number = int(f.read())

    cur_ver_number: int = int(os.environ["DATA_VERSION"])

    if cur_ver_number != old_ver_number:
        from src.db.migration import migrate
        migrate(old_ver_number, cur_ver_number)
        os.system("reboot now")

    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DATABASE_PATH}"
    db.init_app(app)
else:
    from src.db.migration import migrate
    migrate(-1, 0)

    os.system("reboot now")

# Remove whitespace in jinja

app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

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

engine = create_engine(f"sqlite:///{DATABASE_PATH}")

with Session(engine) as session:

    for url in posts:

        n = session.query(PostModel).where(PostModel.id == url).count()
        
        if n == 0:
            db.session.add(
                PostModel(
                    id=url
                )
            )
        else:
            continue
    
    session.commit()

engine.dispose()
del engine

# Sort posts

sorted_items = dict(sorted(posts.items(), key=lambda p: p[1].meta.published.timestamp, reverse=True))
posts.clear()
posts.update(sorted_items)

print(f"Found and loaded {len(posts)} post(s)")

# Import routes
from src.handlers import *

if __name__ == "__main__":
    if os.environ["DEBUG"] == "true":
        app.logger.debug(f"Environment variables: {os.environ}")

        app.run(host="0.0.0.0", port=8000)
    else:
        app.run(host="0.0.0.0", port=8000)