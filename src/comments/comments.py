import os
import sqlite3 as sql
from typing import Any
from flask import render_template
from datetime import datetime
from uuid import uuid4
import html
from flask import request, redirect, session, make_response, abort, render_template_string
from flask_wtf import csrf
from functools import wraps
from argon2 import PasswordHasher

from src.shared import htmx
from src.util import format_datetime
from src.comments import comment_blueprint, Comment, COMMENTS_SCHEMA, DATABASE_PATH, SubmitCommentForm, COMMENTS_ENABLED, LoginForm, FilterCommentsForm, PASSWORD_PATH, DEFAULT_PASSWORD, ChangePasswordForm

SESSION_TIME_LIMIT: int = 60*60

# Init the DB

if not os.path.exists(DATABASE_PATH):
    con = sql.connect(DATABASE_PATH)
    con.execute(COMMENTS_SCHEMA)
    con.close()

# Init password

if not os.path.exists(PASSWORD_PATH):
    ph = PasswordHasher()
    hash = ph.hash(DEFAULT_PASSWORD)

    with open(PASSWORD_PATH, "wb") as pw_file:
        pw_file.write(bytes(hash, encoding="utf-8"))

# Utility methods

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "authenticated" not in session or "time" not in session:
            return redirect("/comments/login")
        else:
            if datetime.now().timestamp() - int(session["time"]) >= SESSION_TIME_LIMIT:
                session["authenticated"] = False
                session["time"] = 0

                return redirect("/comments/login")
        
        return f(*args, **kwargs)
    return decorated_function


def get_comments(slug: str) -> list[Comment]:
    """Returns comments from the database as untreated Comment dataclasses

    Args:
        slug (str): The slug of the post associated with the comments.

    Returns:
        list[Comment]: List of comment dataclasses.
    """
    
    con = sql.connect(DATABASE_PATH)
    con.row_factory = sql.Row
    cur = con.cursor()
    cur = cur.execute("SELECT * FROM comments WHERE parent = ?", (slug, ))
    res: list[dict[str, Any]] = cur.fetchall()

    cur.close()
    con.close()

    if len(res) == 0:
        return []
    
    _comments: list[Comment] = []

    for c in res:
        _comments.append(Comment(**c))
    
    return _comments

def _get_all_comments() -> list[Comment]:
    con = sql.connect(DATABASE_PATH)
    con.row_factory = sql.Row
    cur = con.cursor()

    cur.execute("SELECT * FROM comments")

    res: list[dict[str, Any]] = cur.fetchall()

    cur.close()
    con.close()

    _comments: list[Comment] = [Comment(**c) for c in res]

    for c in _comments:
        c.date = format_datetime(c.date)

    return _comments

# Route methods

@comment_blueprint.route("/comments/post", methods=["POST"])
def _post_comment():

    # Validate form

    form: SubmitCommentForm = SubmitCommentForm()

    comments = get_comments(form.slug.data)

    for c in comments:
        c.date = format_datetime(c.date)

    if not form.validate():
        return render_template(
            "comments.j2", 
            form=form,
            enabled=COMMENTS_ENABLED,
            comments=comments,
        )

    # Connect to database

    con = sql.connect(DATABASE_PATH)
    cur = con.cursor()

    # Generate ID & add record to DB.

    id_found: bool = False
    _id: str = ""

    while not id_found:
        _id = uuid4().hex

        cur.execute("SELECT id FROM comments WHERE id = ?", (_id, ))

        if len(cur.fetchall()) == 0:
            id_found = True
        else:
            continue

    date = datetime.now()
    timestamp = round(date.timestamp())

    cur.execute(
        """INSERT INTO comments (id, name, parent, comment, date) VALUES (?, ?, ?, ?, ?)""",
        (
            _id,
            html.escape(form.name.data),
            form.slug.data,
            html.escape(form.comment.data),
            timestamp
        )
    )
    
    con.commit()

    cur.close()
    con.close()

    # Add submitted comment to list before returning.

    comments = [
        Comment(
            _id,
            html.escape(form.name.data),
            form.slug.data,
            html.escape(form.comment.data),
            format_datetime(timestamp)
        )
    ] + comments

    return render_template(
        "comments.j2",
        form=SubmitCommentForm(),
        comments=comments,
        enabled=COMMENTS_ENABLED
    )

@comment_blueprint.route("/comments/login", methods=["GET", "POST"])
def _comments_login():
    csrf.generate_csrf()

    form: LoginForm = LoginForm()

    if request.method == "GET":
        if htmx:
            return render_template("admin/partials/login.j2", form=form, message="")
        else:
            return render_template("admin/login.j2", form=form, message="")
    elif request.method == "POST":

        if not htmx:
            return abort(400)

        if not form.validate():
            return render_template("admin/partials/login.j2", form=form)
        
        resp = make_response("")
        resp.headers["HX-Location"] = '{"path":"/comments/admin", "target":"#content-block"}'

        session["authenticated"] = True
        session["time"] = datetime.now().timestamp()

        return resp

@comment_blueprint.route("/comments/logout", methods=["POST"])
@login_required
def _comments_logout():
    if not htmx:
        return abort(400)

    session["authenticated"] = False
    session["time"] = 0

    resp = make_response("")
    resp.headers["HX-Redirect"] = "/"

    return resp

@comment_blueprint.route("/comments/admin/delete/<comment_id>", methods=["DELETE"])
@login_required
def _delete_comment(comment_id=None):

    if comment_id == None or not htmx:
        return abort(400)
    
    con = sql.connect(DATABASE_PATH)
    cur = con.cursor()

    # Validate ID

    cur.execute("SELECT id FROM comments WHERE id = ?", (comment_id, ))

    if len(cur.fetchall()) == 0:
        return abort(404)
    
    # does exist so proceed to delete

    cur.execute("DELETE FROM comments WHERE id = ?", (comment_id, ))
    con.commit()

    cur.close()
    con.close()

    return ""

@comment_blueprint.route("/comments/admin/filter", methods=["GET"])
@login_required
def _filter_comments():
    if not htmx:
        return abort(400)
    else:
        form: FilterCommentsForm = FilterCommentsForm(request.args)
        form.validate()

        con = sql.connect(DATABASE_PATH)
        con.row_factory = sql.Row
        cur = con.cursor()

        cur.execute("SELECT * FROM comments WHERE comment LIKE ? OR id == ?", (f"%{form.query.data}%", form.query.data))
        res: list[dict[str, Any]] = cur.fetchall()

        cur.close()
        con.close()

        _comments: list[Comment] = []

        for c in res:
            _comments.append(Comment(**c))
        
        for c in _comments:
            c.date = format_datetime(c.date)

        return render_template_string("""
{%import "admin/partials/comment_row.j2" as row %}

<p id="message" hx-swap-oob="true">{{ results|length }} result(s) for "{{query|escape}}"</p>

<template>

<tbody hx-swap-oob="outerHTML:tbody" hx-confirm="Are you sure?" hx-target="closest tr" hx-swap="outerHTML">
                                      
{% for c in results %}
{{ row.comment_row(c) }}
{% endfor %}

</tbody>

</template>

""", 
        results=_comments, query=form.query.data)
    
@comment_blueprint.route("/comments/admin/changepassword", methods=["POST"])
@login_required
def _admin_change_password():
    
    form: ChangePasswordForm = ChangePasswordForm()

    if not htmx:
        return abort(400)

    if not form.validate():
        return render_template("admin/partials/settings.j2", form=form)
    
    with open(PASSWORD_PATH, "wb") as f:
        ph = PasswordHasher()
        hash = ph.hash(form.new.data)
        f.write(bytes(hash, encoding="utf-8"))

        form = ChangePasswordForm()

        return render_template("admin/partials/settings.j2", form=form, status="Password changed successfully")

@comment_blueprint.route("/comments/admin", methods=["GET"])
@login_required
def _admin_comments():

    form: FilterCommentsForm = FilterCommentsForm()

    if htmx:
        return render_template("admin/partials/admin.j2", comments=_get_all_comments(), form=form)
    else: 
        return render_template("admin/admin.j2", comments=_get_all_comments(), form=form)
    
@comment_blueprint.route("/comments/admin/settings", methods=["GET"])
@login_required
def _admin_settings():
    form: ChangePasswordForm = ChangePasswordForm()

    if htmx:
        return render_template("admin/partials/settings.j2", form=form)
    else:
        return render_template("admin/settings.j2", form=form)