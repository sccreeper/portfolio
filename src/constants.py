import subprocess
from typing import LiteralString

MONTHS = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December"
]

DATABASE_PATH: str = "/var/lib/portfolio/database.db"
DATABASE_SCHEMA: str = """
CREATE TABLE "posts" (
	"slug"	TEXT,
	"views"	INTEGER,
	PRIMARY KEY("slug")
);
"""

APPS_DATA_PATH: str = "/var/lib/portfolio/apps"

DATA_VERSION_PATH: str = "/var/lib/portfolio/data_version.txt"

COMMIT_HASH: LiteralString = subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip()
COMMIT_DATE: LiteralString = subprocess.check_output(["git", "log", "-1", "--format=%ct", "--date=local"]).decode().strip()