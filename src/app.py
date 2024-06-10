from flask import Flask, render_template, abort, send_file, request
from flask_htmx import HTMX
import markdown
import os
from dataclasses import dataclass
import time
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import sqlite3 as sql
import operator
from enum import Enum

from src import APPS_DATA_PATH
from src.caption_extension import ImageCaptionExtension
from src.slideshow_extension import SlideshowExtension
from src.anchor_target_extension import AnchorTargetExtension
from src.header_anchor_extension import HeaderAnchorExtension

DATABASE_PATH: str = "/var/lib/portfolio/posts.db"
DATABASE_SCHEMA: str = """
CREATE TABLE "posts" (
	"slug"	TEXT,
	"views"	INTEGER,
	PRIMARY KEY("slug")
);
"""

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

class SortProp(Enum):
    TIMESTAMP = 1
    TITLE = 2
    LENGTH = 3

class SortDirection(Enum):
    DESC = 1
    ASC = 2

app = Flask(__name__)
htmx = HTMX(app)
posts: list[Post] = []
post_urls: list[str] = []

db: sql.Connection = None
cur: sql.Cursor = None

# Remove whitespace in jinja

app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

# Init database

if not os.path.exists(DATABASE_PATH):
    db = sql.connect(DATABASE_PATH)
    db.execute(DATABASE_SCHEMA)
    cur = db.cursor()
else:
    db = sql.connect(DATABASE_PATH)
    cur = db.cursor()

# Other methods

def post_from_metadata(metadata: dict, url: str, length: int) -> Post:

    t = metadata["published"][0].split("/")

    return Post(
            title=metadata["title"][0],
            summary=metadata["summary"][0],
            authour=metadata["authour"][0],
            tags=metadata["tags"],
            published=metadata["published"][0],
            timestamp=datetime(year=int(t[2]),month=int(t[1]),day=int(t[0])).timestamp(),
            url=url,
            length=length,
        )

# Database update methods

def increase_post_views(slug: str) -> None:
    cur.execute("UPDATE posts SET views = views + 1 WHERE slug = (?)", (slug,))
    db.commit()

def get_post_views(slug: str) -> int:
    cur.execute("SELECT views FROM posts WHERE slug = (?)", (slug,))
    data = cur.fetchone()

    return data[0]

# Register sub-apps

print("Registering apps...")

if not os.path.exists(APPS_DATA_PATH):
    os.mkdir(APPS_DATA_PATH)

from src.apps.random_image import random_image

app.register_blueprint(random_image.random_image_app)

# Load post metadata.

print("Loading post metadata...")

os.chdir("content")

files = os.listdir(".")
files.sort(key=os.path.getmtime)

md = markdown.Markdown(extensions=["meta"])

for f in files:
    if os.path.splitext(f)[1] == ".md":

        post = open(f"{f}", "r")
        text = post.read()
        md.convert(text)
        
        posts.append(
            post_from_metadata(
                md.Meta,
                os.path.splitext(f)[0],
                len(text.split(" ")),   
            )
        )

        post.close()

        post_urls.append(os.path.splitext(f)[0])

    else:
        continue


# Add any new posts to database

for url in post_urls:

    cur.execute("SELECT * FROM posts WHERE slug = (?)", (url,))
    
    if cur.fetchone() == None:
        cur.execute("INSERT INTO posts (slug, views) VALUES (?, ?)", (url, 0))
        db.commit()
    else:
        continue

# Sort posts

posts = sorted(posts, key=operator.attrgetter("timestamp"))
posts.reverse()

print(f"Found and processed {len(posts)} post(s)")

del(md)

os.chdir("..")

@app.route("/", methods=["GET"])
def index():
    post_data = []

    if len(posts) < 3:
        post_data = posts
    else:
        post_data = posts[:3]

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
def blog_post(slug=None):
    if not slug in post_urls:
        return abort(404)
    
    # Parse post

    md = markdown.Markdown(extensions=["meta", "fenced_code", "attr_list", ImageCaptionExtension(), SlideshowExtension(), AnchorTargetExtension(), HeaderAnchorExtension()])
    f = open(f"content/{slug}.md", "r")
    text = md.convert(f.read())
    f.close()

    # Increase post views & get database data.

    increase_post_views(slug)

    post_data = post_from_metadata(md.Meta, slug, 0)

    if htmx:
        return render_template(
            "partials/blogpost.j2", 
            post=post_from_metadata(md.Meta, slug, 0), 
            content=text, 
            views=get_post_views(slug)
        )
     
    else:
        return render_template(
            "blogpost.j2", 
            post=post_data, 
            content=text, 
            title=md.Meta["title"][0], 
            views=get_post_views(slug),
            publish_date=datetime.fromtimestamp(post_data.timestamp).date().isoformat()
        )

@app.route("/content/<path:path>", methods=["GET"])
def blog_content(path=None):
    return send_file(f"../content/{path}")

@app.route("/search", methods=["GET"])
def search():
    start = time.time() * 1000

    query = request.args["query"].lower()
    search_results = []

    for post in posts:
        if (query in post.title.lower() or 
                query in post.summary.lower() or 
                query in [tag.lower() for tag in post.tags]):
            
            search_results.append(post)
    
    if htmx:
        return render_template(
            "partials/search.j2", 
            posts=search_results, 
            time=(time.time() * 1000) - start,
            count=len(search_results)
        )
    
    else:
        return render_template(
                "search.j2",
                posts=search_results,
                time=(time.time() * 1000) - start,
                count=len(search_results)
            )

@app.route("/posts", methods=["GET"])
def _posts():
    # Sort the posts based on form data.

    sort_prop: SortProp
    sort_dir: SortDirection

    if len(request.args) == 0 or not "prop" in request.args or not "dir" in request.args:
        sort_prop = SortProp.TIMESTAMP
        sort_dir = SortDirection.DESC
    else:
        sort_prop = SortProp[request.args["prop"].upper()]
        sort_dir = SortDirection[request.args["dir"].upper()]

    _posts_temp = posts
    _posts_temp.sort(key=operator.attrgetter(sort_prop.name.lower()), reverse=(sort_dir == SortDirection.DESC))

    if htmx:
        return render_template("partials/posts.j2", posts=_posts_temp, count=len(_posts_temp), prop=sort_prop.name.lower(), dir=sort_dir.name.lower())
    else:
        return render_template(
            "posts.j2",
            posts=_posts_temp,
            count=len(_posts_temp),
            prop=sort_prop.name.lower(),
            dir=sort_dir.name.lower()
        )

@app.route("/og/<slug>")
def opengraph(slug=None):
    if not slug in post_urls:
        return abort(404)
    else:
        # Open post MD

        md = markdown.Markdown(extensions=["meta"])
        f = open(f"content/{slug}.md", "r")
        md.convert(f.read())
        f.close()

        p = post_from_metadata(md.Meta, "", 0)

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
        
        return send_file(buffer, mimetype="image/png")

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=8000)