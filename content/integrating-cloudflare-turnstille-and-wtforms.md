Title: Integrating Cloudflare Turnstile and WTForms
Summary: Stop robots messing up your forms
Authour: Oscar Peace
Tags: Cloudflare
      Python
      HTMX
Published: 30/6/2024

WTForms is a library that provides a way in Python to generate the HTML for forms and validate them as well. When combined with Flask, it also includes features such as CSRF protection.

WTForms provides several built in [validators](https://wtforms.readthedocs.io/en/3.1.x/validators/), for example `DataRequired`, `Length`, `EqualTo` and so on. None of these however can provide protection against bots, unless you want to provide a *lot* of code yourself.

This is where Cloudflare Turnstile comes in. Turnstile is an alternative to Google's [reCaptcha](https://developers.google.com/recaptcha/). I tried to find other services but Google seems to have a near monopoly on the market. Searches for ["captcha alternatives"](https://duckduckgo.com/?t=ffab&q=captcha+alternatives&ia=web) just bring up articles written by captcha companies promoting themselves. In the end Turnstile seemed to be the only well supported alternative which is unfortunate if you're trying to avoid big tech.

In order to use Turnstile at all you'll need to get a secret key and a site key from Cloudflare's website. You'll also need a Cloudflare account. I'm assuming if you're reading this article you're reasonably technically competent, so instructions for that are available [here](https://developers.cloudflare.com/turnstile/get-started/).

# Client side

Once you've obtained your secret and site key, you can start making the WTForms widget.

> **Note:** I'm using HTMX here, so the approach is slightly different to a typical fully SSR site.

Firstly you'll need to provide the following script tag:

```html
<script src="https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit"></script>
```

Turnstile provides two "rendering modes". Explicit or implicit. Explicit rendering means that you tell Turnstile where and when to render the widget. In implicit rendering turnstile scans the html for elements with a `cf-turnstile` class and renders it there. As I was using HTMX and needed to re-check the HTML every time a request was made, I used explicit rendering.

The little bit of JavaScript required was as follows:

```js
const turnstileTargetId = "turnstile"

function turnstileInit() {
  let turnstileTarget = document.getElementById(turnstileTargetId);

  if (turnstileTarget) {

    turnstile.ready(function () {
        turnstile.render(`#${turnstileTargetId}`, {
            sitekey: window.cfSiteKey,
            "response-field-name": 'turnstile',
        });
    });

  }
}

turnstileInit();
document.addEventListener("htmx:afterSwap", turnstileInit);
```

- `turnstileTargetId` - Can be anything you want but must be the same as what you've specified in the WTForms widget.
- `htmx:afterSwap` - Every time HTMX performs a swap, re-run this code.
- `function turnstileInit() {...}` - Renders the widget if the target exists on the page. The `window.cfSiteKey` is set in the `base.j2` [template](https://github.com/sccreeper/portfolio/blob/7619cc88c49f5b74a46c9a26b8ed966e64acbcf5/src/templates/base.j2#L23) by the server using a [global context variable](https://github.com/sccreeper/portfolio/blob/7619cc88c49f5b74a46c9a26b8ed966e64acbcf5/src/app.py#L46) set in `app.py`. For testing the site key and secret key were the [dummies](https://developers.cloudflare.com/turnstile/troubleshooting/testing/#dummy-sitekeys-and-secret-keys) provided by Cloudflare.
- Also yes for some reason there are dashes in the property names. I don't know who thought of that to be honest.

# Server side

On the server side you need to validate the Turnstile token, which is submitted by the form and generate the HTML for the turnstile target widget.

As the form would only be rendering a small piece of HTML, I needed a custom widget as well. The widget class takes care of generating the HTML for the field.

```python
class TurnstileTargetWidget:
    turnstile_id: str

    def __init__(self, turnstile_id: str = "turnstile") -> None:
        self.turnstile_id = turnstile_id

    def __call__(self, field: Field, **kwargs: object) -> Markup:
        return Markup(f"<div id='{self.turnstile_id}' {html_params(**kwargs)}></div>")
```
- Implements two methods required to work as a `Widget`.
- The `__init__` method is a standard Python init method, the turnstile ID refers to the id of the div in the HTML, for targeting with the JavaScript mentioned earlier.
- `__call__` is the method used by WTForms to generate the HTML for this widget.

A widget is nothing without it's corresponding field though.

```python
class TurnstileField(Field):
    widget = TurnstileTargetWidget()

    def __init__(self, label: str | None = None, turnstile_id: str = "turnstile", **kwargs) -> None:
        super().__init__(label, [], **kwargs)

        self.widget = TurnstileTargetWidget(turnstile_id=turnstile_id)

    def pre_validate(self, form: BaseForm) -> None:
        super().pre_validate(form)

        validate_turnstile(self.data)
```
- The `self.widget` line in the `__init__` method ensures that no other widget can be set. Otherwise this field wouldn't work and be pointless.
- `pre_validate(...)` - This is called before the other validators and allows the field to perform it's own hardcoded validation logic.
- The `validate_turnstile(...)` method call takes care of calling the Cloudflare API and then raises a `ValidationError` if the token isn't valid.

# Conclusion

Turnstile provides a nice way to check if responses to your forms are genuine which in my case ([comments](/blog/more-blog-updates)) is quite helpful. It was also suprisingly easy to integrate with my existing HTMX-Flask-Jinja-SQLite stack (not really sure about the acronym to be honest) even if did feel a bit hacky to integrate properly with HTMX. Maybe a HTMX captcha extension would be a good idea?