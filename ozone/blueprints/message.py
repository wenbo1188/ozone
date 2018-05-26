from flask import Blueprint, render_template, abort, g, request, redirect, url_for, session
from flask import current_app as app
from jinja2 import TemplateNotFound
from flask_mail import Mail
from flask_mail import Message as mail_message
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

def send_email_to_user(owner: str):
    mail = Mail(app)

    # user1
    if (owner == "汪先森"):
        receiver = app.config['USER2_MAILADDRESS']
    # user2
    else:
        receiver = app.config['USER1_MAILADDRESS']

    sender = ('OZONE消息管家', app.config['MAIL_USERNAME'])
    message_content = owner + "给你留了一条消息，快去看看吧~"
    message = mail_message(message_content, sender = sender, recipients=[receiver])
    mail.send(message)
    # print("send success")

@message_page.route('/')
def show_message():
    if "logged_in" not in session:
        return redirect(url_for("login"))
    with app.app_context():
        db = get_db()
        cur = db.cursor().execute("select timestamp, owner, content from message order by timestamp desc")
        messages = [dict(timestamp=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(row[0])), owner=row[1], content=row[2]) for row in cur.fetchall()]
        # print(messages)
        close_db()
        try:
            return render_template("show_message.html", messages=messages)
        except TemplateNotFound:
            abort(404)

@message_page.route('/add', methods=['POST'])
def add_message():
    owner = None

    # check if log in
    if "logged_in" not in session:
        return redirect(url_for("login"))

    # start add message
    with app.app_context():
        db = get_db()
        timestamp = int(time.time())
        if session["logged_user"] == "wang":
            owner = "汪先森"
        elif session["logged_user"] == "miao":
            owner = "小笨笨"
        else:
            print("Invalid username, something goes wrong!!!")

        db.cursor().execute("insert into message (timestamp, owner, content) values (?, ?, ?)", [timestamp, owner, request.form["content"]])
        db.commit()
        close_db()

        # email reminder
        try:
            send_email_to_user(owner)
        except:
            print("Send email failure")

        try:
            return redirect(url_for("message.show_message"))
        except TemplateNotFound:
            abort(404)

