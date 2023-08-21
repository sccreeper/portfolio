FROM alpine:latest

RUN apk update
RUN apk upgrade

RUN apk add python3 py3-gunicorn poetry npm

WORKDIR /usr/portfolio

COPY . /usr/portfolio/

RUN npm install
RUN poetry install
RUN sh ./build_css.sh

CMD ["poetry", "run", "python3", "-m", "gunicorn", "-b", "0.0.0.0:8000", "src.app:app"]