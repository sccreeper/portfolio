Title: Creating a blog with HTMX and Flask
Summary: The most ideal application you could ever have for HTMX
Authour: Oscar Peace
Tags: Python
      Flask
      HTMX
Published: 18/03/2023

Why [HTMX](https://htmx.org/) for something like a blog? Why not just use something like [Hugo](https://gohugo.io/)/[Jekyll](https://jekyllrb.com/) or if you wanted to be on the "bleeding edge" of web development, use something that would be almost certainly be overkill like SvelteKit or Next.js?. Because HTMX and a light web framework such as [Flask](https://flask.palletsprojects.com) can achieve everything those libraries and applications can with much less hassle. Also I like making stuff myself and HTMX is cool.

Adding the first page to my blog was pretty simple, this was just a case of copying my old website code, converting it into [Jinja templates](https://jinja.palletsprojects.com/en/3.1.x/) with a base template and a partial home template and setting up Tailwind CSS.

```

{# The full file for the homepage that extends base.j2 using the partial file for home.j2 #}

{% extends "base.j2" %}

{% block head %}
<meta property="og:title" content="Oscar Peace"/>
<meta property="og:description" content="Home"/>
{% endblock head %}

{% block title %} Home {% endblock title %}

{% block content %}

{% with posts=posts %}
{% include "partials/home.j2" %}
{% endwith %}

{% endblock content %}

```

# Adding more pages

Adding more pages to my website was just as easy, all I had to do was create a `projects.j2` file and use the same approach I had applied before on the server:

- Has the request come from HTMX?
- If yes, we return the `render_template` of just the `projects.j2`.
- If no we return the complete webpage to the browser.

![](/content/assets/navigation%20with%20HTMX.gif "Page navigation with HTMX")
<figcaption>Page navigation with HTMX</figcaption>

Then using the [hx-swap-oob](https://htmx.org/attributes/hx-swap-oob/) attribute, which allows you to swap any element on the web page not just the one specified in the `hx-select` on the element that triggers the HTMX request, I could change things like the page title in the header as well. This removes the need to write any client-side DOM manipulation code whatsoever. **HTMX controls all.**

```html
<title hx-swap-oob="outerHTML:title">title text here</title>
```

# Viewing a blog post

Viewing blog posts was very simple to add.

At runtime I scanned through the content directory for Markdown files and and parsed them using the Python `markdown` library with it's `meta` extension. This allowed me to create a dictionary of all the posts in memory without having to read the disk anytime I wanted information about the posts.

When a user visited the site I would then render the summaries (title, date published, byline etc.) of the first n posts on the homepage.

When one of these summaries was clicked, HTMX would send a request to the server and as before would swap out the content block of the page with the server response.

![](/content/assets/viewing%20blog%20post.gif "First blog post view")
<figcaption>First blog post view</figcaption>

# Search

This was the most advanced use of HTMX so far and what you would traditionally be more suited to a framework like Svelte or React (🤢), especially if you wanted it to be automatically update whenever a user inputs. But HTMX can do all of that anyway so who cares.

```html
<input type="text" placeholder="Search" name="query"
hx-trigger="keyup change delay:250ms"
hx-push-url="true"
hx-target="#content-block"
hx-get="/search"
/>
```

The above code sends a GET request to the server with the content of the search box 250ms after the last user input (this timer is reset every time the user inputs), then the response is swapped into the `#content-block` div. The GET request to the server follows the format:
```
/search?query=Hello%20World
```
The response is then a list of posts that contain whatever the user has inputted.

![](/content/assets/search.gif "Searching")

<figcaption>Searching</figcaption>

# Conclusion

After I finished adding all the necessary features I added:

- [Open graph](https://ogp.me/) metadata, using [Pillow](https://python-pillow.org/) to generate summary images on the fly.
- Better printer styling (removing border styles and making the page wider etc.)
- And page tags.

In conclusion this was probably one of the easiest web development experiences I've ever had, which makes sense as HTMX isn't too difficult and Python is just pseudocode and I will definitely keep HTMX in mind for projects in the future, it is a very useful tool to have in my toolbox.