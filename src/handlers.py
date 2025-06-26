from flask import render_template, abort, send_from_directory, send_file, request

from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import operator
from flask_wtf import FlaskForm
from wtforms.fields import SelectField, StringField, HiddenField
import mimetypes
from flask_wtf import csrf

from src._dataclasses import DateContainer, PostMeta
from src.shared import posts, htmx, cache, app
from src.feeds import feed_registry
from src.comments import SubmitCommentForm, get_comments, COMMENTS_ENABLED
from src.db.models import PostModel
from src.db import db
from src.util import htmx_cache_key
from werkzeug.exceptions import HTTPException, InternalServerError, NotFound, Forbidden, TooManyRequests

def handle_exception(e: HTTPException):
    return render_template(
        "error.j2",
        error_code=e.code,
        error_message=e.description
    ), e.code

for err in (InternalServerError, NotFound, Forbidden, TooManyRequests):
    app.register_error_handler(err, handle_exception)

@app.route("/", methods=["GET"])
@cache.cached(make_cache_key=lambda: htmx_cache_key(False), timeout=0)
def index():
    post_meta: list[PostMeta] = []

    if len(posts) < 3:
        post_meta = [v.meta for i, (k, v) in enumerate(filter(lambda x: not x[1].meta.unlisted, posts.items()))]
    else:
        post_meta = [v.meta for i, (k, v) in enumerate(filter(lambda x: not x[1].meta.unlisted, posts.items())) if i < 3]

    if htmx:
        return render_template("partials/home.j2", posts=post_meta)
    else:
        return render_template(
            "home.j2",
            posts=post_meta 
        )

@app.route("/projects", methods=["GET"])
@cache.cached(make_cache_key=lambda: htmx_cache_key(False), timeout=0)
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

    db.session.query(PostModel).\
        where(PostModel.id == slug).\
        update({"views": PostModel.views + 1})
    db.session.commit()

    post = db.session.get(PostModel, slug)

    form: SubmitCommentForm = SubmitCommentForm()
    form.slug.data = slug

    comments: list = get_comments(slug)
    comments = sorted(comments, key=operator.attrgetter("date"), reverse=True)

    for c in comments:
        c.date = DateContainer.create_date(c.date)

    sim_posts: list[tuple[PostMeta, int]] = []

    for p in posts:
        if p == slug:
            continue
        else:
            common = set(posts[p].meta.tags) & set(posts[slug].meta.tags)

            if len(common) == 0:
                continue
            else:
                sim_posts.append((posts[p].meta, len(common)))

    # Sort by number of common tags, then truncate
    sim_posts = sorted(sim_posts, key=lambda x: x[1])
    sim_posts.reverse()
    sim_posts = sim_posts[0:3]
    
    if htmx:
        return render_template(
            "partials/blogpost.j2", 
            post=posts[slug].meta,
            sim_posts=sim_posts,
            content=posts[slug].body, 
            views=post.views,
            comments=comments,
            form=form,
            comments_enabled=COMMENTS_ENABLED,

        )
     
    else:
        return render_template(
            "blogpost.j2", 
            post=posts[slug].meta, 
            sim_posts=sim_posts,
            content=posts[slug].body, 
            title=posts[slug].meta.title, 
            views=post.views,
            comments=comments,
            comments_enabled=COMMENTS_ENABLED,
            form=form
        )

@app.route("/content/<path:path>", methods=["GET"])
def blog_content(path=None):
    return send_from_directory("../content/", path)

class PostsForm(FlaskForm):
    class Meta:
        csrf = False

    prop = SelectField("Sort by: ", choices=[("timestamp", "Date"), ("title", "Title"), ("length", "Length")], default="timestamp", coerce=str)
    dir = SelectField("Direction: ", choices=[("asc", "Ascending"), ("desc", "Descending")], default="desc", coerce=str)

    tags = StringField("Tags: ", default="", render_kw={"placeholder" : "python, go"})

    query = StringField("Search: ", default="", render_kw={"placeholder" : "A post"})

@app.route("/posts", methods=["GET"])
@cache.cached(make_cache_key=lambda: htmx_cache_key(True), timeout=0)
def _posts():
    # Sort the posts based on form data.

    form: PostsForm = PostsForm(request.args)

    if not form.validate():
        form.process()

    # Filter based on search query

    if not form.query.data == "":
        # Worst list comprehension ever written.
        _posts_temp = [\
            post for post in [v.meta for v in list(posts.values())] if form.query.data.lower() in post.title.lower() or form.query.data.lower() in [tag.lower() for tag in post.tags]
        ]
    else:
        _posts_temp = [v.meta for v in list(posts.values())]

    # Filter based on tags

    if len(form.tags.data.split(",")) > 1: # for some reason splitting an empty string still returns an array with 1 item

        tag_set: set[str] = {t.lower() for t in [s.strip() for s in form.tags.data.split(",")]}

        _posts_temp = [v.meta for v in list(posts.values()) if len({t.lower() for t in v.meta.tags} & tag_set) == len(tag_set)]

    _posts_temp.sort(
        key=operator.attrgetter(
            form.prop.data if form.prop.data != "timestamp" else "published.timestamp"
         ), 
        reverse=(form.dir.data == "desc")
    )

    # Remove unlisted posts
    _posts_temp = list(filter(lambda x: not x.unlisted, _posts_temp))

    if htmx:
        return render_template("partials/posts.j2", posts=_posts_temp, count=len(_posts_temp), form=form)
    else:
        return render_template(
            "posts.j2",
            posts=_posts_temp,
            count=len(_posts_temp),
            form=form
        )

@app.route("/og/<slug>", methods=["GET"])
@cache.cached(make_cache_key=lambda: htmx_cache_key(False), timeout=0)
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
            f"{p.published.date_mmddyyyy}",
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
@cache.cached(timeout=0)
def _feeds(feed_type: str = None):

    if not feed_type in feed_registry:
        return abort(404)

    buffer = BytesIO()
    buffer.write(
        feed_registry[feed_type].generate_feed(
            [v for v in list(filter(lambda x: not x.meta.unlisted, posts.values()))][:5]
        )
    )
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name=feed_registry[feed_type].file,
        mimetype=mimetypes.types_map[feed_registry[feed_type].extension]
    )