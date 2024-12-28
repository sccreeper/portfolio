from src.constants import DATABASE_PATH
import sqlite3 as sql
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from src.db.models import BaseModel, CommentModel, PostModel
from typing import Any
from dataclasses import dataclass
from datetime import datetime

_POSTS_DB_PATH = "/var/lib/portfolio/posts.db"
_COMMENTS_DB_PATH = "/var/lib/portfolio/comments.db"

@dataclass
class _Comment:
    id: str
    name: str
    parent: str
    comment: str
    date: int

# This is the initial migration from raw SQL to SQLAlchemy I wrote.
# It was very stupid to not make any migration system or use SQLAlchemy originally. Oh Well.

def migrate():
    
    # Create new database
    engine = create_engine(f"sqlite:///{DATABASE_PATH}", echo=True)
    # create_database(engine.url)
    BaseModel.metadata.create_all(engine)

    # Migrate existing data

    con = sql.connect(_POSTS_DB_PATH)
    con.row_factory = sql.Row
    cur = con.cursor()

    # Migrate posts

    cur.execute("SELECT * FROM posts")

    rows: list[dict[str, Any]] = cur.fetchall()

    with Session(engine) as session:
        for r in rows:
            session.add(
                PostModel(
                    id=r["slug"],
                    views=r["views"]
                )
            )
        
        session.commit()

    cur.close()
    con.close()

    # Migrate comments

    con = sql.connect(_COMMENTS_DB_PATH)
    con.row_factory = sql.Row
    cur = con.cursor()

    cur.execute("SELECT * FROM comments")

    rows: list[dict[str, Any]] = cur.fetchall()

    cur.close()
    con.close()

    _comments: list[_Comment] = [_Comment(**c) for c in rows]

    with Session(engine) as session:
        for c in _comments:
            session.add(
                CommentModel(
                    post=c.parent,
                    name=c.name,
                    comment=c.comment,
                    date=datetime.fromtimestamp(c.date)
                )
            )

        session.commit()

    engine.dispose()

    