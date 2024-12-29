from datetime import datetime
from flask import request as req
from dataclasses import dataclass

from src.shared import htmx

def format_datetime(timestamp: float) -> str:
    """Returns 'mm:ss - yyyy:mm:dd' formatted date

    Args:
        timestamp (float): POSIX timestamp

    Returns:
        str: Formatted date string
    """

    d = datetime.fromtimestamp(timestamp)

    return f"{d.hour:0>2}:{d.second:0>2} — {d.year:0>4}-{d.month:0>2}-{d.day:0>2}"

CF_IP_HEADER: str = "CF-Connecting-IP"

def get_real_ip() -> str:
    """Gets user IP. Some logic required to figure out if behind Cloudflare or not.

    Args:
        req (Request): The request object to be checked.

    Returns:
        str: Resulting IP
    """

    if CF_IP_HEADER in req.headers:
        return req.headers[CF_IP_HEADER]
    else:
        return req.remote_addr
    
def htmx_cache_key():
    return f"{req.path}:{'htmx' if htmx else 'not_htmx'}"
