Title: URL Shortener with Flask and HTMX
Summary: A tiny app that can be recreated in a weekend 
Authour: Oscar Peace
Tags: Python
    Programming
    Flask
    HTMX
Published: 07/07/2025

It's been a while since I've made anything new with HTMX. The last thing was the [comment section](/blog/more-blog-updates) for this blog, which itself [is made](/blog/making-a-blog-with-flask-and-htmx) using Flask and HTMX. TLDR; I like using Flask and HTMX. Something I've always wanted to have is some kind of link shortening service. I'm well aware that services like bit.ly and Tiny URL exist however in my opinion it's much better to have something of your own especially when it's incredibly simple to make.

While I could've used a fullstack framework for this, e.g. Svelte, I already had some experience using Flask and HTMX together now and I wanted to see how quickly I could create something usable. In the end it turned out that I was indeed able to create something rather quickly. 

Since I had already chosen Flask and HTMX the only remaining decision was what database engine to use. This ended up being SQLite for the same reasons mentioned before, ease of use, familiarity etc. This project was essentially the biggest case of why you shouldn't reinvent the wheel, something I have done too many times already, using new stacks for projects where the scope just isn't worth it, and later coming to regret it as a result.

The codebase was then hammered together using the same outline I had figured out when I added comments to this blog, with some minor improvements - having data migration from the start and correct use of indexes. In the end while the thing I ended up with was rather ugly because I didn't use any CSS bar some for colouring @red error messages @, choosing to stick to the principles of [justfuckingusehtml.com](https://justfuckingusehtml.com/) instead.

I also added a JSON API which used the same routes as the HTMX, just expecting and returning JSON instead of form data and HTML respectively. No need for another backend server when you have `if` statements and schemas.

![](/content/assets/signpost%20admin%20ui.png "Zoomed in screenshot of the admin UI")

Opaque means wether or not to return a 301 redirect response or to return a small JavaScript snippet to do the redirection. This means that any link previews won't work when it's enabled. Useful for creating rick roll links.

You can test it for yourself now by clicking on [this link](https://ospe.lol/o7JU) which redirects to this blogpost.

The source for the project itself can be found [here](https://github.com/sccreeper/signpost) on GitHub.