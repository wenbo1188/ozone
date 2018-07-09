from flask import Blueprint, render_template, abort, g, request, redirect, url_for, session
from flask import current_app as app
from jinja2 import TemplateNotFound
import sqlite3
import time
from reminder_util import EmailReminder 

column_page = Blueprint("column", __name__, template_folder="templates")

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

@column_page.route('/')
def show_essay():
    if "logged_in" not in session:
        return redirect(url_for("login"))
    with app.app_context():
        db = get_db()
        cur = db.cursor().execute("select timestamp, owner, title, content from essay order by timestamp desc")
        essays = [dict(timestamp=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(row[0])), owner=row[1], title=row[2], content=row[3], collapse_id=row[0]) for row in cur.fetchall()]
        # print(essays)
        close_db()
        try:
            return render_template("show_essay.html", essays=essays)
        except TemplateNotFound:
            abort(404)

@column_page.route('/add', methods=['POST'])
def add_essay():
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

        print(request.form["title"], request.form["content"])

        db.cursor().execute("insert into essay (timestamp, owner, title, content, user1_read, user2_read) values (?, ?, ?, ?, 0, 0)", [timestamp, owner, request.form["title"], request.form["content"]])
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
        message_content = "An essay has been updated, go and have a look~"

        reminder = EmailReminder(app.config['MAIL_SERVER'], app.config['MAIL_PORT'], app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'], False)
        try:
            reminder.send(receiver, receiver_name, message_content)
        except:
            print("Send email failure")

    try:
        return redirect(url_for("column.show_essay"))
    except TemplateNotFound:
        abort(404)

