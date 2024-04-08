#!/bin/bash
npx tailwindcss -i ./src/static/index.css -o ./src/static/dist.css --minify

# Build for components
npx tailwindcss -i ./src/static/slideshow.css -o ./src/static/slideshow-dist.css --minify

rm ./src/static/index.css
rm ./src/static/slideshow.css