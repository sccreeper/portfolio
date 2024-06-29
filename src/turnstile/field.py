from markupsafe import Markup
from wtforms import Field, Form
from wtforms.widgets import html_params
from typing import Callable

from src.turnstile.turnstile import _validate

# CF turnstile field. Created specifically for use on this website.

class TurnstileTargetWidget:
    turnstile_id: str

    def __init__(self, turnstile_id: str = "turnstile") -> None:
        self.turnstile_id = turnstile_id

    def __call__(self, field: Field, **kwargs: object) -> Markup:
        return Markup(f"<div id='{self.turnstile_id}' {html_params(**kwargs)}></div>")

class TurnstileField(Field):
    widget = TurnstileTargetWidget()

    def __init__(self, label: str | None = None, turnstile_id: str = "turnstile", validators: list[Callable[[Form, Field], None]] = None, **kwargs) -> None:
        super().__init__(label, validators, **kwargs)

        if validators is None:
            self.validators = []
        self.validators.append(_validate)

        self.widget = TurnstileTargetWidget(turnstile_id=turnstile_id)
