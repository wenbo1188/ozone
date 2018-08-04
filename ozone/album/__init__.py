from flask import Blueprint

album_page = Blueprint("album", __name__, template_folder="template")

from . import views