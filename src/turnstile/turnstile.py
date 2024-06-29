import requests
import os
import json
from wtforms import ValidationError, Form, Field

from src import app

CF_URL: str = "https://challenges.cloudflare.com/turnstile/v0/siteverify"

CF_SECRET: str = os.environ["CF_TURNSTILE_SECRET"]

def _validate(form: Form, ts_field: Field):

    resp = requests.post(
        CF_URL,
        {
            "secret": CF_SECRET,
            "response" : ts_field.data,
        }
    )

    app.logger.debug(resp.text)
    app.logger.debug(ts_field.data)
    resp = json.loads(resp.content)

    if not resp["success"] == True:
        raise ValidationError("Captcha failed. Please try again.")

