Title: Python-Markdown extensions and web components
Summary: MDX more like MDN
Authour: Oscar Peace
Tags: Markdown
      Python
      Web-Components
      JavaScript
Published: 20/4/2024

For a while now I've wanted to create something with web components. The problem is that I've been too addicted too [SvelteKit](https://kit.svelte.dev/)/[Svelte](https://svelte.dev/) (I'm not blaming Svelte here, it's just also [quite good](/blog/earth-mc-dashboard)) to use them for anything where I wouldn't also try to just use plain old vanilla JavaScript instead. 

However, the real problem is that, I wanted to try and keep this blog as JavaScript free (JavaScript bloat mostly) as possible. All my existing posts (there were only about five of them to be fair) were written in plain Markdown, and I didn't (I still don't) even want to touch [MDX](https://mdxjs.com/) or React with a mile long pole.

Mainly I just have an incredibly strong aversion to using React.

This led me to the solution of using a Markdown extension written in Python and implementing it on the client with Web Components.

Yes, this kind of violates the ethos so far of trying to keep stuff as "vanilla" and JavaScript free as possible however the way I eventually implemented it tries to abide by that as much as possible. I hope so anyway or maybe I'm just deluded.

# The extension

There are two main parts to this post, writing the Python extension and then writing the web components part. If you don't care about the Python implementation then you can skip this part.

Getting a foundation to base the extension off of wasn't too bad, as the [Python-Markdown](https://python-markdown.github.io/) library provides several examples for the different extension types.

In this case I would be writing a `BlockProcessor` extension which would recognise the syntax in the "half-parsed" markdown and then add elements to the element tree. 

If some of that sounds a bit daunting to you then don't worry, I'll explain it in due course.

## What is a block processor?

***TLDR;** block processors work with blocks. well duh?*

> A block processor parses blocks of text and adds new elements to the `ElementTree`.

A block in Python Markdown is essentially just a paragraph. After the parser has been through and removed all the comments, whitespace and then separated the text by newlines into paragraphs, you are left with blocks.

It is useful for whenever you want to add something new to markdown that involves some additional syntax.

Then you can run a regex (I love & hate regex, It's just difficult sometimes) expression until you find the beginning of your special block, your fence.

It should be noted that you don't necessarily have to look for some kind of fence expression. It's just that's what probably works best for something like a block processor.

When you have found the start of your fence, you can then process the blocks inside of it until you find the end of it, at which point you stop processing and add whatever HTML you have created to the element tree.

The element tree is almost the final representation of what the rendered document will look like. It is in essence just what it says on the tin. A tree of the elements in the markdown document. In the block processor you can add/remove elements from it and even modify existing ones.

More information on the element tree can be found [here](https://python-markdown.github.io/extensions/api/#working_with_et).

More information about the block processor can be found [here](https://python-markdown.github.io/extensions/api/#working_with_et)

## Writing the extension

Firstly I needed to decide on what my "fence" expression and my overall syntax was going to look like.

The example used here is a slideshow as this is ultimately what I ended up creating:

```markdown

# other post stuff

a paragraph

<!-- The sideshow data -->

////

/images/slide1.png The first slide
/images/slide2.png The second slide

////

```

Processing this once I had found the fences was reasonably simple. The documentation provided an example which already did half of wanted to achieve so I used that as my starting point.

```python

class SlideshowBlockProcessor(BlockProcessor):

    # Regex fences

    RE_FENCE_START = r'^\/{4}'
    RE_FENCE_END = r'\/{4}$'

    def test(self, parent, block):
        return re.match(self.RE_FENCE_START, block)

    def parse_slides(self, blocks: list[str]) -> list[Slide]:
      ...

    def run(self, parent, blocks):
      ...

```

Above is a skeleton version of what I implemented, the original can be found in the [repository](https://github.com/sccreeper/portfolio/blob/df84a0e5f09bffe568b80e4bf4b99f373fdfe467/src/slideshow_extension.py).


*Some explaining:*

1. The regex fences. These are just regex expressions as constants used to find the start/end of the slideshow data.
2. [`test()`](https://github.com/sccreeper/portfolio/blob/df84a0e5f09bffe568b80e4bf4b99f373fdfe467/src/slideshow_extension.py#L19) - This is not actually a method to test if the extension actually works but rather it exists so the markdown library can "test" it on each block, and if the method returns true, then that block (and subsequent blocks if necessary) is processed by the extension.
3. [`parse_slides()`](https://github.com/sccreeper/portfolio/blob/df84a0e5f09bffe568b80e4bf4b99f373fdfe467/src/slideshow_extension.py#L22) - This is a utility function used to convert each line within the fence to a `Slide` dataclass.
Below is the dataclass:
```python
@dataclass
class Slide:
  src: str
  caption: str
```
4. `run()` - This method is run if the `test()` method returns `True`. From this you can modify, add or remove elements from the element tree. This block also takes responsibility for managing where the end of the fence is. See [here](https://github.com/sccreeper/portfolio/blob/df84a0e5f09bffe568b80e4bf4b99f373fdfe467/src/slideshow_extension.py#L38) for full implementation.

Define our original block in case we need to replace it when no end fence is found. Also replace the first fence with whitespace.

```python
original_block = blocks[0]
blocks[0] = re.sub(self.RE_FENCE_START, '', blocks[0])
```

Loop through the blocks and process each one using the `parse_slides` method. Then add corresponding elements to the element tree and return `True`.

**Note:** The `if` statement means that this only runs *if* the end fence is found at the very start using regex.

```python
for i, block in enumerate(blocks):
    if re.search(self.RE_FENCE_END, block):

        # Remove fence
        blocks[i] = re.sub(self.RE_FENCE_END, '', block)

        # Create slideshow parent element

        s: list[Slide] = self.parse_slides(blocks[0:i+1])

        slideshow = etree.SubElement(parent, "slide-show")

        for j, slide in enumerate(s):
            slideshow.insert(j, etree.Element("slide", slide.__dict__))

        # Remove URL and caption blocks
        for j in range(0, i+1):
            blocks.pop(0)

        return True
```

If the fence isn't found then replace the original block and return `False`, as we haven't done anything.

```python
blocks[0] = original_block
return False

```

# The web component

***If you are using this as a guide and have skipped ahead to this bit, I would still recommend reading the extension part as this section assumes that you have.***

If you're expecting documentation on web components that's as comprehensive as a more popular way of creating reusable JavaScript bundles then good luck. 

To be fair I knew I would probably have to pay a small early adopters tax, even though these have been a thing since 2020 according to [MDN](https://developer.mozilla.org/en-US/docs/Web/API/Web_Components), but that doesn't outweigh how easy they were to use.

Anyway that's a small rant out of the way.

## What is a web component?

According to MDN a web component (which is also sort of a custom element) is a

> set of JavaScript APIs that allow you to define custom elements and their behavior, which can then be used as desired in your user interface

For a slightly less concise explanation:

1. You create a JS class that extends another element, this can be the base `HTMLElement` or a `ParagraphElement` etc.
2. Then you add specific "life cycle callbacks" to that class. The most important ones being he `connectedCallback` and the `attributeChangedCallback`.
3. In the connected callback, which is invoked when the the element is first recognised by the browser and added to the DOM, you construct the element's shadow DOM (a semi-isolated DOM within the document DOM), using a template or `document.addElement`.
4. Finally at the bottom of the class/file you add the element to the element registry.

## My slideshow element

The basic markup for the slideshow element was as follows:

```html

<slide-show>

  <slide caption="Slide 1" src="image_for_slide_1.png"></slide>
  <slide caption="Slide 2" src="image_for_slide_2.png"></slide>
  <!-- etc. -->

</slide-show>

```

As you can see there is the main `<slide-show>` (custom elements have to have a dash in their name) element and the `<slide>` (these aren't custom elements) elements inside it. My main aim was for it to be as close to "vanilla" HTML as possible.

My job now was to use JavaScript to take the HTML outputted by the markdown parser and turn into something actually useful.

## The JavaScript

For the purposes of readability I'm not including the full source here so instead you can look at it on GitHub [here](https://github.com/sccreeper/portfolio/blob/df84a0e5f09bffe568b80e4bf4b99f373fdfe467/src/static/scripts/components/slideshow.js).


```js

class Slide {

    constructor(caption, src) {
        this.caption = caption;
        this.src = src;
    }

}

```

This was a very simple class which would created from the `<slide>` elements, just to contain the caption and src.

```js

class SlideshowElement extends HTMLElement {

    slides;
    currentSrc;

    constructor() {
        super();
    }

    nextSlide() {
      // ...
    }
    
    get currentSlide() {
      // ...
    }

    set currentSlide(val) {
      // ...
    }

    _generateNumbers() {
      // ...
    }

    connectedCallback() {
        // ...
    }

}

```

- `nextSlide` - Literally what it says on the tin.
- The getters and setters. The only special part of these is that they're used to actually update the DOM and therefore make those changes shown to the user.
- `_generateNumbers` - Not really much to say. Returns an array of spans with the current selected slide a `<b>` element instead.
- `connectedCallback` - The most important method here. As mentioned before this takes care of doing the initialising of the custom element. More information about it is below.

> Shadow DOM enables you to attach a DOM tree to an element, and have the internals of this tree hidden from JavaScript and CSS running in the page.

\- *[MDN](https://developer.mozilla.org/en-US/docs/Web/API/Web_components/Using_shadow_DOM)*

This of course is great for something like web components because it means you can do whatever you really want in it's own context, without the pesky main document really getting in the web.

If you've ever used something like Svelte, the best thing I could compare this to is the HTML section of your component file, bearing in mind that you can construct it using a `<template>` element or JavaScript directly.

After reading the documentation more it certainly provides a much less cumbersome way to use the `<template>` element in a useful way anyway.

The other major setup that takes place in this method is retrieving the child `<slide>` elements and adding their properties to the `slides` property.

Finally the element is added to the element registry with it's corresponding class and tag names with:

```javascript
customElements.define("slide-show", SlideshowElement)
```

# Integration

Fortunately integration was the easiest part of this process. 

All I had to do after writing the Python to generate the HTML and the JavaScript to make said HTML actually do something was just include the required script tag in my page and everything worked.

**Disclaimer:** There were actually a few small bugs I had to fix beforehand and throughout making this. Not everything is perfect.

# Conclusion

In conclusion, do web components have a bright future ahead of them? Yes. Are they easy to integrate and use? Yes. Do they have the same adoption and support as something like Svelte? No, but I believe it will only be a matter of time. Hopefully we don't get something stupid like a framework that converts to web components before then.

The full code used and mentioned in this post can be found on the GitHub repo for this blog.