import requests
import os
import json
from wtforms import ValidationError, Form, Field

from src import app

CF_URL: str = "https://challenges.cloudflare.com/turnstile/v0/siteverify"

CF_SECRET: str = os.environ["CF_TURNSTILE_SECRET"]

def validate_turnstile(ts_token: str):

    resp = requests.post(
        CF_URL,
        {
            "secret": CF_SECRET,
            "response" : ts_token,
        }
    )

    app.logger.debug(resp.text)
    app.logger.debug(ts_token)
    resp = json.loads(resp.content)

    if not resp["success"] == True:
        raise ValidationError("Captcha failed. Please try again.")

