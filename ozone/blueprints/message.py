from flask import Blueprint, render_template, abort, g, request, redirect, url_for, session
from flask import current_app as app
from jinja2 import TemplateNotFound
import sqlite3
import time
from reminder_util import EmailReminder

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

@message_page.route('/<int:page>')
def show_message(page=1):
    if "logged_in" not in session:
        return redirect(url_for("login"))

    with app.app_context():
        db = get_db()
        num_per_page = app.config['MESSAGE_PER_PAGE']

        # get total num of messages
        cur = db.cursor().execute("select count(*) from message")
        num = cur.fetchall()[0][0]
        if (num % num_per_page == 0):
            max_page = int(num / num_per_page)
        else:
            max_page = int((num / num_per_page) + 1)
        # print(num, max_page)
        
        if ((page - 1) * num_per_page >= num):
            print("Illegal page number")
            page = max_page

        if (page <= 0):
            print("Illegal page number")
            page = 1

        cur = db.cursor().execute("select timestamp, owner, content from message order by timestamp desc limit ? offset ?", [num_per_page, (page - 1) * num_per_page])
        messages = [dict(timestamp=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(row[0])), owner=row[1], content=row[2]) for row in cur.fetchall()]
        # print(messages)
        close_db()
        try:
            return render_template("show_message.html", messages=messages, total_page=max_page, current_page=page)
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
        if (owner == "汪先森"):
            receiver = app.config['USER2_MAILADDRESS']
            receiver_name = app.config['USERNAME2']
        elif (owner == "小笨笨"):
            receiver = app.config['USER1_MAILADDRESS']
            receiver_name = app.config['USERNAME1']
        else:
            print("Invalid username, something goes wrong!!!")
        message_content = "A new message for you, go and have a look~"

        reminder = EmailReminder(app.config['MAIL_SERVER'], app.config['MAIL_PORT'], app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'], False)
        try:
            reminder.send(receiver, receiver_name, message_content)
        except:
            print("Send email failure")

        try:
            return redirect(url_for("message.show_message"))
        except TemplateNotFound:
            abort(404)

