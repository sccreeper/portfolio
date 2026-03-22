import os
import markdown
from src.mdextensions import *
from src._dataclasses import PostData, PostMeta, DateContainer
from datetime import datetime
import pickle

from markdown.extensions.meta import MetaExtension
from markdown.extensions.fenced_code import FencedCodeExtension
from markdown.extensions.tables import TableExtension
from markdown.extensions.footnotes import FootnoteExtension

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

    # Load post metadata.

    print("Generating posts...")

    os.chdir("content")

    files = os.listdir(".")
    files.sort(key=os.path.getmtime)

    md = markdown.Markdown(
            extensions=[
                MetaExtension(), 
                FencedCodeExtension(),
                TableExtension(),
                FootnoteExtension(BACKLINK_TEXT="^", SUPERSCRIPT_TEXT="[{}]"),
                SlideshowExtension(), 
                AnchorTargetExtension(), 
                HeaderAnchorExtension(),
                ImageProcessorExtension(),
                ColourExtension(),
                IconExtension(),
                MathsExtension()
                ]
            )

    for f in files:
        slug, ext = os.path.splitext(f)

        if ext == ".md":

            print(f"Generating {slug}")

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

        else:
            continue

    pass

if __name__ == "__main__":
    main()