# portfolio

The source for my portfolio website and blog at [www.oscarcp.net](https://www.oscarcp.net). The engine is custom, and includes some extra markdown stuff and comments. The license for the engine is MIT however I wouldn't recommend trying to adapt it to your own needs. It would be much more worthwhile to look at the code, see how it works, and then go on to write a better version.

# License

Everything under the `src` folder is under an MIT license (see `LICENSE_ENGINE`) as well as associated software files in the root directory. Files in the `content` directory fall under CC-BY-4.0 (`LICENSE_CONTENT`), apart from those where fair use/dealing may be a concern - files where this is a concern are marked with a  `.fd.` in their extension suffix accordingly.

# Project layout

- `content` - Contains all blogposts and their associated assets (images, documents etc.).
- `src` - contains the source code for the blog engine.
    - `apps` - Sub-apps/extensions for the engine.
    - `comments` - Provides functionality for the addition and moderation of comments under blogposts.
    - `db` - All code for interacting with the database (shared between posts and comments) utilising SQLAlchemy.
    - `feeds` - Utilities for generating RSS, Atom and JSON feeds.
    - `mdextensions` - Extensions to the markdown renderer to provide additional functionality.
    - `static`- Static files: scripts, images, and stylesheets.
    - `templates` - Jinja files
    - `turnstile`- Provides Cloudflare turnstile functionality for forms.
    - `app.py` - Main entrypoint.
    - `generate.py` - Handles the initial generation and processing of markdown files when the Docker image is built.