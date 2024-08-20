FROM alpine:3.20

RUN apk update
RUN apk upgrade

RUN apk add python3 py3-gunicorn poetry npm gcc libffi-dev python3-dev musl-dev
RUN apk add imagemagick libavif libpng libjpeg libheif

WORKDIR /usr/portfolio

COPY . /usr/portfolio/

RUN npm install
RUN poetry install
RUN sh ./build_css.sh

RUN poetry run python3 -m src.generate

CMD ["sh", "./run.sh"]