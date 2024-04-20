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

from src import APPS_DATA_PATH
from src.caption_extension import ImageCaptionExtension
from src.slideshow_extension import SlideshowExtension
from src.anchor_target_extension import AnchorTargetExtension

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

app = Flask(__name__)
htmx = HTMX(app)
posts: list[Post] = []
post_urls: list[str] = []

db: sql.Connection = None
cur: sql.Cursor = None

# Init database

if not os.path.exists(DATABASE_PATH):
    db = sql.connect(DATABASE_PATH)
    db.execute(DATABASE_SCHEMA)
    cur = db.cursor()
else:
    db = sql.connect(DATABASE_PATH)
    cur = db.cursor()

# Other methods

def post_from_metadata(metadata: dict, url: str) -> Post:

    t = metadata["published"][0].split("/")

    return Post(
            title=metadata["title"][0],
            summary=metadata["summary"][0],
            authour=metadata["authour"][0],
            tags=metadata["tags"],
            published=metadata["published"][0],
            timestamp=datetime(year=int(t[2]),month=int(t[1]),day=int(t[0])).timestamp(),
            url=url
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
        md.convert(post.read())
        post.close()
        
        posts.append(post_from_metadata(
            md.Meta,
            os.path.splitext(f)[0]
            
        ))

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

    md = markdown.Markdown(extensions=["meta", "fenced_code", "attr_list", ImageCaptionExtension(), SlideshowExtension(), AnchorTargetExtension()])
    f = open(f"content/{slug}.md", "r")
    text = md.convert(f.read())
    f.close()

    # Increase post views & get database data.

    increase_post_views(slug)


    if htmx:
        return render_template("partials/blogpost.j2", post=post_from_metadata(md.Meta, slug), content=text, views=get_post_views(slug))
    else:
        return render_template(
            "blogpost.j2", 
            post=post_from_metadata(md.Meta, f"{slug}"), 
            content=text, 
            title=md.Meta["title"][0], 
            views=get_post_views(slug)
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
    if htmx:
        return render_template("partials/posts.j2", posts=posts, count=len(posts))
    else:
        return render_template(
            "posts.j2",
            posts=posts,
            count=len(posts)
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

        p = post_from_metadata(md.Meta, "")

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
    app.run(host="0.0.0.0",port=8000,debug=True)