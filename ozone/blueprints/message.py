from flask import Blueprint, render_template, abort, g, request, redirect, url_for, session
from flask import current_app as app
from jinja2 import TemplateNotFound
import sqlite3
import time

message_page = Blueprint("message", __name__, template_folder="templates")

def connect_db():
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def get_db():
    if not hasattr(g, 'sqlite3_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

def close_db():
    if hasattr(g, 'sqlite3_db'):
        g.sqlite_db.close()

@message_page.route('/')
def show_message():
    if "logged_in" not in session:
        return redirect(url_for("login"))
    with app.app_context():
        db = get_db()
        cur = db.cursor().execute("select timestamp, owner, content from message order by timestamp desc")
        messages = [dict(timestamp=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(row[0])), owner=row[1], content=row[2]) for row in cur.fetchall()]
        print(messages)
        try:
            return render_template("show_message.html", messages=messages)
        except TemplateNotFound:
            abort(404)
        close_db()

@message_page.route('/add', methods=['POST'])
def add_message():
    with app.app_context():
        db = get_db()
        timestamp = int(time.time())
        db.cursor().execute("insert into message (timestamp, owner, content) values (?, ?, ?)", [timestamp, request.form["owner"], request.form["content"]])
        db.commit()
        try:
            return redirect(url_for("message.show_message"))
        except TemplateNotFound:
            abort(404)
        close_db()

