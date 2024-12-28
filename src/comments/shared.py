from flask import Blueprint
import os

PASSWORD_PATH: str = "/var/lib/portfolio/password.bin"
DEFAULT_PASSWORD: bytes = b"password"

COMMENTS_ENABLED: bool = (os.environ["COMMENTS"] == "true")
print(f"Comments enabled: {COMMENTS_ENABLED}")

comment_blueprint = Blueprint("comments", __name__,  template_folder="templates")
