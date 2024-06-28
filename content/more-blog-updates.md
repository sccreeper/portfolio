Title: Adding comments to this blog
Summary: I love HTMX and WTF-Forms
Authour: Oscar Peace
Tags: Programming
      HTMX
      Python
      Flask
Published: 28/6/2024

# Why?

For a while now I've wanted to have some form of feedback on this blog. 

There are already view-counts for each page, but this isn't really accurate, and you can't really tell much from a number. Initially this made me think about adding an "upvotes" system or something similar. Then again this is still a number. Then I had only one option left, comments so I set about implementing them using my sites existing stack, (HTMX + Flask + Python).

# The database

Firstly, If you're going to have data, you need to store it somewhere right? For this you need a database.

I was already using SQLite for the views database, and as I don't expect this to have incredibly high traffic I'll keep using it.

SQLite can scale reasonably well, it is used to power the [SQLite website](https://sqlite.org/index.html) after all, which also states that it can handle "100K hits per day", and I don't expect to be getting near that. That figure could be a bit biased as well to be fair, but then again [nobody lies](https://en.wikipedia.org/wiki/Volkswagen_emissions_scandal) about benchmarks right?

If needed in the future, I can hopefully upgrade it to something like [PostgreSQL](https://www.postgresql.org/).

The schema I settled on included the ID, the comment's parent (leading room for replies in the future) which at the moment is just the slug of post it is under, the time, name and comment text.

# Posting comments

So far the only forms on the website weren't exactly complicated as they only included the filtering & sorting options on the [posts](/posts) page. 

This wasn't practical for posting comments where I needed to add validation and there would need to be multiple other forms as well.

This led me to actually following Flask "best practice" for once, because as a self taught programmer I never have any idea if what I'm doing is really correct, and using the [Flask-WTF](https://flask-wtf.readthedocs.io/en/1.2.x/) forms extension.

The extension integrates the WTForms library with Flask, providing important features like CSRF protection and server-side and basic client side validation.

For posting comments I needed a simple form class and a custom validator for filtering out profanity. When I say profanity I mean swear words plus the stuff that's a lot more vulgar.

```python
from flask_wtf import FlaskForm

class SubmitCommentForm(FlaskForm):
    
    name = StringField(
        None, 
        render_kw={"placeholder": "Name"}, 
        validators=[
            DataRequired("Name is required"), 
            Length(4, 32, "Names must be between 4 and 32 characters long."),
            profanity_validator
        ]
    )
    
    comment = StringField(
        None, 
        render_kw={"placeholder": "Comment", "rows": "3"}, 
        validators=[
            DataRequired("Comment is required"), 
            Length(1, 512, "Comments have a maximum length of 512 characters."),
            profanity_validator
        ],
        widget=TextArea(),
    )

    slug = HiddenField(None, validators=[_slug_validator])
```

As you can see there are several fields, with properties set in the arguments. The slug field just exists to determine which post this is being posted on.

Both the name and comment fields have the `profanity_validator` attached. This deals with any simple occurrences of profanity using a list of words, symbols and exceptions. Humans can always get around filters though and they're not always 100% accurate (See the [Scunthorpe problem](https://en.wikipedia.org/wiki/Scunthorpe_problem) and Tom Scott's [video](https://youtu.be/CcZdwX4noCE) for more info).

This should block most instances of people using profanity however in the likely case they are able to get around it, I also built a simple moderation view.

I should be able to add [Cloudflare's Turnstile](https://developers.cloudflare.com/turnstile/) quite easily in the future if I want to.

# Moderating comments

Just in case anything slipped through the aforementioned profanity filter, I still needed a way to ~~moderate~~ delete comments. 

## Authentication

Now I know you should "never roll your own auth", however in this case it's probably okay, as there is only ever one user, me. Initially I just stored the password in a plaintext environment variable (bad idea) with the authentication verified using the Flask `session` variable, which is [reasonably secure](https://blog.miguelgrinberg.com/post/how-secure-is-the-flask-user-session).

Even though (and hear me out) storing the password like this was okay at the start, as if somebody got access to the server, then I would just be completely fucked either way because the sever secret would be exposed as well, but because I was going to deploy this properly, just in case I decided to change to using `argon2` instead as it was at the top of OWASP's [list](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html#argon2id) of recommended libraries and had a nice [library](https://pypi.org/project/argon2-cffi/) with Python.

This for some reason felt like it took the longest to do, probably because I wasted a good half hour wondering why the hash wasn't parsing correctly and raising an `InvalidHashError` only to realise I was reading the database file in as the stored hash and not the password hash file.

## Moderation

The only tool I needed for moderation was a delete button. Fortunately this was easy to implement with HTMX and some basic Jinja templating:

```django
<tr id="{{ data.id }}">

    <td>{{ data.id }}</td>
    <td>{{ data.parent }}</td>
    <td>{{ data.date }}</td>
    <td>{{ data.name }}</td>
    <td>{{ data.comment|truncate(32, True) }}</td>

    <td>
        <button hx-delete="/comments/admin/delete/{{ data.id }}">Delete</button>
        <a href="/blog/{{ data.parent }}#c-{{ data.id }}" target="_blank">View</a>
    </td>

</tr>
```

The `data` variable was a comment [dataclass](https://docs.python.org/3/library/dataclasses.html).

The `truncate` [filter](https://jinja.palletsprojects.com/en/3.0.x/templates/#filters) also takes care of truncating the comment so the table doesn't get all messed up as well.

The `hx-confirm` attribute also takes care of a prompt, so no extra JavaScript is needed.

////

/content/assets/comments%20post/comments%20admin%20zoomed%20in.png The final admin view (ignore the complete lack of CSS). I kind of like the 90s spartan HTML look as well.

/content/assets/comments%20post/comments%20settings%20zoomed%20in.png The settings view

////

The filter (query) and logout features are also built with HTMX as well.

![](/content/assets/comments%20post/filter%20demo.gif "Filter demonstration")

# Conclusion

Hopefully now (if everything is working as it should) you should now be able to add comments beneath this post. If I add any updates in the future, e.g. turnstile and maybe replies, then I'll add it on at the end of this post.