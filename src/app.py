from flask import Flask, render_template, abort, send_file, request
from flask_htmx import HTMX
import markdown
import os
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import sqlite3 as sql
import operator
from flask_wtf import FlaskForm
from wtforms.fields import SelectField, StringField
import mimetypes

from src import APPS_DATA_PATH, Post, post_slugs, posts
from src.caption_extension import ImageCaptionExtension
from src.slideshow_extension import SlideshowExtension
from src.anchor_target_extension import AnchorTargetExtension
from src.header_anchor_extension import HeaderAnchorExtension
from src.rss import generate_rss_feed, POST_LIMIT

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

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ["SECRET"]

htmx = HTMX(app)

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

        post_slugs.append(os.path.splitext(f)[0])

    else:
        continue


# Add any new posts to database

con = sql.connect(DATABASE_PATH)
cur = con.cursor()

for url in post_slugs:

    cur.execute("SELECT * FROM posts WHERE slug = (?)", (url,))
    
    if cur.fetchone() == None:
        cur.execute("INSERT INTO posts (slug, views) VALUES (?, ?)", (url, 0))
        con.commit()
    else:
        continue

con.close()

# Sort posts

posts = sorted(posts, key=operator.attrgetter("timestamp"), reverse=True)
post_slugs.reverse()

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
    if not slug in post_slugs:
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

@app.route("/posts", methods=["GET"])
def _posts():
    # Sort the posts based on form data.

    form: PostsForm = PostsForm(request.args)

    if not form.validate():
        form.process()

    if not form.query.data == "":
        app.logger.debug("test")
        # Worst list comprehension ever written.
        _posts_temp = [post for post in posts if form.query.data.lower() in post.title.lower() or form.query.data.lower() in [tag.lower() for tag in post.tags]]
    else:
        _posts_temp = posts

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
    if not slug in post_slugs:
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
        
        return send_file(buffer, mimetype=mimetypes.types_map[".png"])

@app.route("/rss", methods=["GET"])
def _rss():
    buffer = BytesIO()
    buffer.write(generate_rss_feed(posts[:POST_LIMIT]))
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="rss.xml",
        mimetype=mimetypes.types_map[".xml"]
    )

if __name__ == "__main__":
    if os.environ["DEBUG"] == "true":
        app.run(host="0.0.0.0",port=8000, debug=True)
    else:
        app.run(host="0.0.0.0",port=8000)