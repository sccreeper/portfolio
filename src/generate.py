import os
import markdown
from src.mdextensions import *
from src._dataclasses import PostData, PostMeta, DateContainer
from datetime import datetime
import pickle
from pygments.formatters import HtmlFormatter

from markdown.extensions.meta import MetaExtension
from markdown.extensions.fenced_code import FencedCodeExtension
from markdown.extensions.tables import TableExtension
from markdown.extensions.footnotes import FootnoteExtension
from markdown.extensions.codehilite import CodeHiliteExtension

def post_from_metadata(metadata: dict, url: str, length: int) -> PostMeta:

    t = metadata["published"][0].split("/")

    return PostMeta(
            title=metadata["title"][0],
            summary=metadata["summary"][0],
            authour=metadata["authour"][0],
            tags=metadata["tags"],
            published=DateContainer.create_date(
                datetime(year=int(t[2]),month=int(t[1]),day=int(t[0])).timestamp()
            ),
            slug=url,
            unlisted=url[0] == '.',
            length=length,
        )

def main():

    # Do code CSS
    styles = HtmlFormatter(style="monokai").get_style_defs(".highlight")

    with open("src/static/code.css", 'w') as f:
        f.write(styles)

    # Load post metadata.

    print("Generating posts...")

    os.chdir("content")

    files = os.listdir(".")
    files.sort(key=os.path.getmtime)

    md = markdown.Markdown(
            extensions=[
                MetaExtension(), 
                FencedCodeExtension(),
                CodeHiliteExtension(guess_lang=False, css_class="highlight"),
                TableExtension(),
                FootnoteExtension(BACKLINK_TEXT="^", SUPERSCRIPT_TEXT="[{}]"),
                SlideshowExtension(), 
                AnchorTargetExtension(), 
                HeaderAnchorExtension(),
                ImageProcessorExtension(),
                ColourExtension(),
                IconExtension(),
                MathsExtension(),

                ]
            )
    
    # Count number of markdown files for progress
    num_markdown = 0

    for f in files:
        _, ext = os.path.splitext(f)

        if ext == ".md":
            num_markdown += 1
    
    num_processed = 0

    for f in files:
        slug, ext = os.path.splitext(f)

        if ext == ".md":

            print(f"\033[K{round((num_processed/num_markdown)*100)}% - Generating {slug}...", end="\r", flush=True)

            post = open(f"{f}", "r")
            text = post.read()
            body = md.convert(text)

            p = PostData(
                meta=post_from_metadata(
                    md.Meta,
                    slug,
                    len(text.split(" ")),   
                ),
                body=body
            )

            md.reset()

            with open(f"{slug}.pkl", "wb") as pklf:
                pickle.dump(p, pklf)
            
            post.close()

            num_processed += 1

        else:
            continue

    pass

if __name__ == "__main__":
    main()