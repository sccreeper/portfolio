FROM alpine:latest

RUN apk update
RUN apk upgrade

RUN apk add python3 py3-gunicorn poetry npm

WORKDIR /usr/portfolio

COPY . /usr/portfolio/

RUN npm install
RUN poetry install
RUN sh ./build_css.sh

CMD ["sh", "./run.sh"]