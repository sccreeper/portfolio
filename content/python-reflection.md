Title: "Reflection" in Python
Summary: Don't do this to yourself.
Authour: Oscar Peace
Tags: Python
    Programming
Published: 04/01/2025

My university's first year (introductory) programming module has a series of worksheets you complete to introduce you to Python. The worksheets consist of questions wherein each question is answered with a separate function. Of course now in order to test the answer to each question, I needed to append the name at the end of the file and then run it. I could do this for every function and question or write a wrapper, because I had time to fill, I decided on the wrapper.

This wrapper would then examine each of the files and list the functions, the arguments and then need to know the types of those arguments, which would then require examining the type hints. All this analysis would essentially end up being "reflection" or more so type introspection.

# How to do reflection

> "reflective programming or reflection is the ability of a process to examine, introspect, and modify its own structure and behavior."
>
> \- [Wikipedia](https://en.wikipedia.org/wiki/Reflective_programming)

Python is a dynamic language. This means that variables aren't always what they say to each other so to speak. You can even do something totally unhinged and attach a [new method to a class](https://stackoverflow.com/a/2982). Yes a class, and at the same time applying it to every other instance of said class. Why do I choose to work with this godforsaken language?

Despite it's lack of sensibility it seems to make up for it with some features that were added later on. One of these features are type hints. Type hints, "hint" to a language server/IDE/etc. about what the type of a variable *should be*.

> The Python runtime does not enforce function and variable type annotations. They can be used by third party tools such as type checkers, IDEs, linters, etc.
>
> \- [Documentation](https://docs.python.org/3/library/typing.html) 

Some examples of type hints are show below:

```python
x: list[int] # Integer list
y: str #  Literally just a string
z: dict[str, int] # Dictionary 
```

There are some more complicated types available from the built-in [typing](https://docs.python.org/3/library/typing.html) library, but the ones listed above will be fine for now.

## Getting the functions in the file

The first thing I had to do was get the list of functions available in any file. This part was quite easy, I had already decided upon a naming convention for each week so I just had to loop through all the files and then get the functions:

```python
import importlib
import inspect

func_module = importlib.import_module(f"worksheet1.py")

method_list = inspect.getmembers(func_module, isfunction)

```

The variable `method_list` only contains references to those functions - a bit similar to if you were to do something like:

```python

def foo():
    pass

print(foo)
# <function foo at 0x7f43644662a0>

```

With this reference to `foo` we can get certain attributes, i.e. it's name and docstring (yes I'll get onto that later), but we still need to do some extra work in order to find out it's arguments and type hints.

At this point I could have just stopped and started using the built-in eval function but this is [bad](https://stackoverflow.com/questions/1832940/why-is-using-eval-a-bad-practice) for a number of reasons, mostly security related, and it also felt like cheating as in my case there was definitely a "better way" of doing it.

## Getting arguments

Before we can get any type hints, we must first determine if a function has parameters. To do this we get the "signature" of the function and then retrieve it's parameters.

```python

import importlib
import inspect

func_module = importlib.import_module("worksheet1.py")

method_list = inspect.getmembers(func_module, isfunction)

func_sig = inspect.signature(method_list[0][1])
print(func_sig.parameters)

```

Now we have the parameters of the function we can loop through all of them and determine what type they are and handle it accordingly.

## Getting type hints

Getting the type hint can simply be achieved by accessing the `annotation` attribute of the type value (each value in the `parameters` list is a tuple) of each parameter returned from `func_sig.parameters`.

The type hint on it's own is pretty useless for our needs as it's just a type object and we need the class/object of the type for casting, not just it's type representation. We can do this as follows:

```python
import typing
import inspect

def foo(bar: str):
    pass

func_sig = inspect.signature(foo)
anno = func_sig.parameters["bar"].annotation

print(typing.get_origin(anno))
# <class 'str'> instead of 'str'
```

Now armed with the "origin" of the type hint we can do type casting or perform different actions if we come across a `list` parameter.

# Putting it all together

All of the things mentioned above do nothing on their own per say. Now I needed to create something that was actually useful, that is a "runner" for all my worksheets.

The logical process isn't complicated, it just uses all the things mentioned above, the steps it follows are listed below:

1. Get the all the functions in a file, then print them out.
2. The user enters a number that corresponds to a function, the arguments of the chosen function are then asked for one-by-one.
3. If the type of the argument is a list then we ask for each list element before pressing Ctrl+C, other arguments only once and casting appropriately.
4. Finally call the function.

The full code is available here as a [GitHub gist](https://gist.github.com/sccreeper/8e39485d694e5d6daab2f0cb45db7bca). If you want to use it yourself then you must adhere to the following directory layout:

```shell
|- run.py
|- week1
    |- pract1.py
|- week2
    |- question_one.py
    |- anyname.py
```

Each week can either have one `practN.py` file or multiple files. In the case of each of multiple files each is treated as a separate "program".

# Conclusion

I don't think I would do this again in a hurry, however it was a nice sort of introduction into some of the more weird parts of Python. I've got object oriented programming coming up so I'll adapt it to work with class constructors and some more complex argument types.