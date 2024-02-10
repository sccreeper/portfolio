Title: Adding Flask blueprints & other improvements
Summary: Other little bits I want to put on my website
Authour: Oscar Peace
Tags: Flask
      Python
Published: 10/2/2024

One of my favorite things about other people's websites is the little mini-games and apps that they add, however with the way I had made my website there wasn't a way to add this whilst keeping the core reusable for other purposes. 

The solution?

*Flask blueprints.*

A blueprint in Flask is equivalent to something like a plugin. It allows you to import an external module (or in this case technically internal) and register routes that are handled by that module.

That module basically works as a normal `flask.App()`:

```py
from flask import Blueprint

my_plugin = Blueprint("my_plugin", __name__)

#Then register the routes you want to handle 
#Similar to how they are registered using annotations in normal Flask.

@my_plugin.route("/my_plugin route")
def test_route():
      return 'Hello World'
```

The route registered behaves and can be used in the same way as any other Flask route.

Then in your main Flask app you can import and use it as follows:

```py
from plugins.my_plugin import my_plugin

app.register_blueprint(my_plugin.my_plugin)
```

If you want them to behave similar to plugins, you can set something up to scan the directory and import them all automatically (You can import modules dynamically in Python using [importlib](https://docs.python.org/3/library/importlib.html#importlib.import_module)). However, I would recommend a file just listing which ones should be enabled or not.

```py
import importlib

my_plugin = importlib.import_module('plugins.my_plugin')
```

In practice this would add all the modules to a dictionary or something similar instead of storing them in a single variable.

In the future I would like to write and Flask apps in a plugin style, especially ones which aren't monolithic in nature (this blog is monolithic, so it won't work), e.g. a backend for an API or something where the frontend and backend are both written using Flask (a bit of HTMX maybe), but the backend needs to be accessible from other clients.

In my opinion blueprints are an honestly amazing and overlooked feature of Flask that have so many great use-cases.