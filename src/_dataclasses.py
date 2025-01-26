from dataclasses import dataclass
from datetime import datetime
from typing import Self

from src.constants import MONTHS

# Shared dataclasses

@dataclass
class DateContainer:
    """
    Wrapper around `datetime.datetime` in order to provide some extra formats.
    """
    timestamp: float
    date_8601: str
    date_full: str
    date_mmddyyy: str
    iso_full: str
    time: str

    @staticmethod
    def create_date(ts: float | datetime) -> Self:
        dt = ts
        if type(ts) is float:
            dt = datetime.fromtimestamp(ts)

        return DateContainer(
            timestamp=dt.timestamp(),
            date_8601=f"{dt.year}-{dt.month:02}-{dt.day:02}",
            date_mmddyyy=f"{dt.day:02}/{dt.month:02}/{dt.year}",
            date_full=f"{dt.day} {MONTHS[dt.month-1]} {dt.year}",
            time=f"{dt.hour:02}:{dt.minute:02}",
            iso_full=dt.isoformat()
        )

# Post only dataclasses
@dataclass(order=True)
class PostMeta():
    title: str
    summary: str
    authour: str
    tags: list[str]
    published: DateContainer
    slug: str
    unlisted: bool

    length: int

@dataclass
class PostData:
    meta: PostMeta
    body: str