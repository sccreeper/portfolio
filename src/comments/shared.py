from flask import Blueprint
from dataclasses import dataclass
import os

DATABASE_PATH: str = "/var/lib/portfolio/comments.db"
COMMENTS_SCHEMA = """
CREATE TABLE "comments" (
	"id"	TEXT,
	"name"	TEXT,
	"parent"	TEXT,
	"comment"	TEXT,
    "date" INTEGER,
	PRIMARY KEY("id")
)
"""

PASSWORD_PATH: str = "/var/lib/portfolio/password.bin"
DEFAULT_PASSWORD: bytes = b"password"

COMMENTS_ENABLED: bool = (os.environ["COMMENTS"] == "true")
print(f"Comments enabled: {COMMENTS_ENABLED}")

comment_blueprint = Blueprint("comments", __name__,  template_folder="templates")

@dataclass
class Comment:
    id: str
    name: str
    parent: str
    comment: str
    date: int