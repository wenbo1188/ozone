from flask import Blueprint

main_page = Blueprint("main", __name__, template_folder="templates")

from . import views
