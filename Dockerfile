FROM alpine:3.21

RUN apk update
RUN apk upgrade

RUN apk add python3 py3-gunicorn poetry npm gcc libffi-dev python3-dev musl-dev git
RUN apk add imagemagick libavif libpng libjpeg libheif

WORKDIR /usr/portfolio

COPY ./poetry.lock ./pyproject.toml ./package.json ./package-lock.json /usr/portfolio/

RUN npm install
RUN poetry install

COPY . /usr/portfolio/

RUN sh ./build_css.sh

ENV PYTHONUNBUFFERED=1
RUN poetry run python3 -m src.generate

CMD ["sh", "./run.sh"]