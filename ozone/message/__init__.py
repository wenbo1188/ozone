from flask import Blueprint

message_page = Blueprint("message", __name__, template_folder="templates")

from . import views
