from flask import render_template, abort, send_from_directory, send_file, request
import logging
import pickle
import os
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import sqlite3 as sql
import operator
from flask_wtf import FlaskForm
from wtforms.fields import SelectField, StringField
import mimetypes
from flask_wtf import csrf
from flask_limiter import Limiter
from flask_compress import Compress

from src import APPS_DATA_PATH, PostData, posts, htmx
from src.feeds import feed_registry
from src.util import format_datetime, get_real_ip

DATABASE_PATH: str = "/var/lib/portfolio/posts.db"
DATABASE_SCHEMA: str = """
CREATE TABLE "posts" (
	"slug"	TEXT,
	"views"	INTEGER,
	PRIMARY KEY("slug")
);
"""

class PostsForm(FlaskForm):
    class Meta:
        csrf = False

    prop = SelectField("Sort by: ", choices=[("timestamp", "Date"), ("title", "Title"), ("length", "Length")], default="timestamp", coerce=str)
    dir = SelectField("Direction: ", choices=[("asc", "Ascending"), ("desc", "Descending")], default="desc", coerce=str)

    query = StringField("Search: ", default="", render_kw={"placeholder" : "Search"})

from src import app
app.config["SECRET_KEY"] = os.environ["SECRET"]

@app.context_processor
def inject_cf_keys():
    return dict(cfsitekey=os.environ["CF_TURNSTILE_SITE_KEY"])

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

# Database update methods

def increase_post_views(slug: str) -> None:
    con = sql.connect(DATABASE_PATH)
    cur = con.cursor()

    cur.execute("UPDATE posts SET views = views + 1 WHERE slug = (?)", (slug,))
    con.commit()

    con.close()

def get_post_views(slug: str) -> int:
    con = sql.connect(DATABASE_PATH)
    cur = con.cursor()

    cur.execute("SELECT views FROM posts WHERE slug = (?)", (slug,))
    data = cur.fetchone()

    con.close()

    return data[0]

# Register sub-apps

print("Registering apps...")

if not os.path.exists(APPS_DATA_PATH):
    os.mkdir(APPS_DATA_PATH)

from src.apps.random_image import random_image

app.register_blueprint(random_image.random_image_app)

from src.comments import comment_blueprint, get_comments, SubmitCommentForm, COMMENTS_ENABLED

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

posts = {k: v for k, v in sorted(posts.items(), key=lambda item: item[1].meta.timestamp, reverse=True)}

print(f"Found and loaded {len(posts)} post(s)")

@app.route("/", methods=["GET"])
def index():
    post_data = []

    if len(posts) < 3:
        post_data = [v.meta for v in list(posts.values())]
    else:
        post_data = [v.meta for v in list(posts.values())[:3]]

    if htmx:
        return render_template("partials/home.j2", posts=post_data)
    else:
        return render_template(
            "home.j2",
            posts=post_data 
        )

@app.route("/projects", methods=["GET"])
def projects():
    if htmx:
        return render_template("partials/projects.j2")
    else:
        return render_template("projects.j2")

@app.route("/blog/<slug>", methods=["GET"])
def blog_post(slug: str=None):
    if not slug in posts:
        return abort(404)
    
    csrf.generate_csrf()

    # Increase post views & get database data.

    increase_post_views(slug)

    form: SubmitCommentForm = SubmitCommentForm()
    form.slug.data = slug

    comments: list = get_comments(slug)
    comments = sorted(comments, key=operator.attrgetter("date"), reverse=True)

    for c in comments:
        c.date = format_datetime(c.date)
    
    if htmx:
        return render_template(
            "partials/blogpost.j2", 
            post=posts[slug].meta, 
            content=posts[slug].body, 
            views=get_post_views(slug),
            comments=comments,
            form=form,
            comments_enabled=COMMENTS_ENABLED,

        )
     
    else:
        return render_template(
            "blogpost.j2", 
            post=posts[slug].meta, 
            content=posts[slug].body, 
            title=posts[slug].meta.title, 
            views=get_post_views(slug),
            publish_date=datetime.fromtimestamp(posts[slug].meta.timestamp).date().isoformat(),
            comments=comments,
            comments_enabled=COMMENTS_ENABLED,
            form=form
        )

@app.route("/content/<path:path>", methods=["GET"])
def blog_content(path=None):
    return send_from_directory("../content/", path)

@app.route("/posts", methods=["GET"])
def _posts():
    # Sort the posts based on form data.

    form: PostsForm = PostsForm(request.args)

    if not form.validate():
        form.process()

    if not form.query.data == "":
        # Worst list comprehension ever written.
        _posts_temp = [post for post in [v.meta for v in list(posts.values())] if form.query.data.lower() in post.title.lower() or form.query.data.lower() in [tag.lower() for tag in post.tags]]
    else:
        _posts_temp = [v.meta for v in list(posts.values())]

    _posts_temp.sort(key=operator.attrgetter(form.prop.data), reverse=(form.dir.data == "desc"))

    if htmx:
        return render_template("partials/posts.j2", posts=_posts_temp, count=len(_posts_temp), form=form)
    else:
        return render_template(
            "posts.j2",
            posts=_posts_temp,
            count=len(_posts_temp),
            form=form
        )

@app.route("/og/<slug>")
def opengraph(slug=None):
    if not slug in posts:
        return abort(404)
    else:

        p = posts[slug].meta

        # Create and draw on image

        buffer = BytesIO()

        img = Image.new("RGB", (848, 480), color=(0, 0, 0))
        draw = ImageDraw.Draw(img)

        draw.text(
            (16, 175),
            p.title,
            fill=(255, 255, 255),
            font=ImageFont.truetype("src/static/fonts/FiraMono-Regular.ttf", size=32)
        )

        draw.text(
            (16, 224),
            f"{p.published}",
            fill=(255, 255, 255),
            font=ImageFont.truetype("src/static/fonts/FiraMono-Bold.ttf", size=18)
        )

        draw.rectangle(
            (
                (8, 8), 
                (840, 472)
            )
        )
        
        img.save(buffer, "PNG")
        buffer.seek(0)
        
        return send_file(buffer, mimetype=mimetypes.types_map[".png"])

@app.route("/feeds/<feed_type>", methods=["GET"])
def _feeds(feed_type: str = None):

    if not feed_type in feed_registry:
        return abort(404)

    buffer = BytesIO()
    buffer.write(feed_registry[feed_type].generate_feed([v.meta for v in list(posts.values())][:5]))
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name=feed_registry[feed_type].file,
        mimetype=mimetypes.types_map[feed_registry[feed_type].extension]
    )

if __name__ == "__main__":
    if os.environ["DEBUG"] == "true":
        app.logger.debug(f"Environment variables: {os.environ}")

        app.run(host="0.0.0.0",port=8000, debug=True)
    else:
        app.run(host="0.0.0.0",port=8000)