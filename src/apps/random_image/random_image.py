from flask import Blueprint, send_file
from src.constants import APPS_DATA_PATH
import os
import random
import json

DEFAULT_CONFIG: dict = {
    "url" : "random_image"
}

APP_PATH: str = f"{APPS_DATA_PATH}/random_image"
APP_CONFIG: str = f"{APP_PATH}/config.json"
image_files: list = []

config = DEFAULT_CONFIG

random_image_app = Blueprint("random_image_extension", __name__)

if not os.path.exists(APP_PATH):
    os.mkdir(APP_PATH)

if not os.path.exists(APP_CONFIG):
    f = open(APP_CONFIG, "w")
    f.write(json.dumps(DEFAULT_CONFIG))
    f.close()
else:
    f = open(APP_CONFIG, "r")
    config = json.loads(f.read())
    f.close()

image_files = [f for f in os.listdir(APP_PATH) if os.path.isfile(os.path.join(APP_PATH, f)) and f != "config.json"]

@random_image_app.route(f"/{config['url']}")
def show_image():
    if len(image_files) == 0:
        return ""
    else:
        return send_file(f"{APP_PATH}/{random.choice(image_files)}")