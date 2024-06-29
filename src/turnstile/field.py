from markupsafe import Markup
from wtforms import Field, Form
from wtforms.widgets import html_params
from typing import Callable

from src.turnstile.turnstile import validate_turnstile

# CF turnstile field. Created specifically for use on this website.

class TurnstileTargetWidget:
    turnstile_id: str

    def __init__(self, turnstile_id: str = "turnstile") -> None:
        self.turnstile_id = turnstile_id

    def __call__(self, field: Field, **kwargs: object) -> Markup:
        return Markup(f"<div id='{self.turnstile_id}' {html_params(**kwargs)}></div>")

class TurnstileField(Field):
    widget = TurnstileTargetWidget()

    def __init__(self, label: str | None = None, turnstile_id: str = "turnstile", **kwargs) -> None:
        super().__init__(label, [], **kwargs)
        
        # having other validators messes up the CF logic.
        # they're not needed anyway because this is a completely custom field.
        self.validators = [validate_turnstile]

        self.widget = TurnstileTargetWidget(turnstile_id=turnstile_id)
