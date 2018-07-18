from flask import Blueprint

column_page = Blueprint("column", __name__, template_folder="templates")

from . import views
