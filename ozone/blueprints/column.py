from flask import Blueprint, render_template, abort, g, request, redirect, url_for, session
from flask import current_app as app
from jinja2 import TemplateNotFound
from flask_mail import Mail
from flask_mail import Message as mail_message
import sqlite3
import time
import threading
from email.mime.text import MIMEText
from email.header import Header
import smtplib

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

def split_paragraph(text: str) -> list:
    return text.split("\r\n")

def send_async_email(msg, mail_username, mail_password, mail_server, to_addr, mail_port, debug = False):
    server = smtplib.SMTP_SSL(mail_server, mail_port)
    if (debug):
        server.set_debuglevel(1)

    try:
        server.login(mail_username, mail_password)
    except:
        print("fail to login")

    server.sendmail(mail_username, [to_addr], msg.as_string())
    server.quit()

def send_email_to_user(owner: str):
    #user1
    if (owner == "汪先森"):
        receiver = app.config['USER2_MAILADDRESS']
        receiver_name = app.config['USERNAME2']
    # user2
    else:
        receiver = app.config['USER1_MAILADDRESS']
        receiver_name = app.config['USERNAME1']

    mail_username = app.config['MAIL_USERNAME']
    mail_password = app.config['MAIL_PASSWORD']
    mail_server = app.config['MAIL_SERVER']
    mail_port = app.config['MAIL_PORT']

    #message_content = owner + "更新了专题，快去看看吧~"
    message_content = "An essay has been updated, go and have a look~"
    message = MIMEText(message_content, 'text', 'utf-8')
    message['Subject'] = Header("Ozone消息提醒", 'utf-8')
    message['From'] = 'Ozone消息管家<13188316906@163.com>'
    message['To'] = receiver_name + '<' + receiver + '>'

    mail_thread = threading.Thread(target = send_async_email, args = [message, mail_username, mail_password, mail_server, receiver, mail_port])
    mail_thread.start()
    #mail.send(message)
    # print("send success")

@column_page.route('/')
def show_essay():
    if "logged_in" not in session:
        return redirect(url_for("login"))
    with app.app_context():
        db = get_db()
        cur = db.cursor().execute("select timestamp, owner, title, content from essay order by timestamp desc")
        essays = [dict(timestamp=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(row[0])), owner=row[1], title=row[2], content=split_paragraph(row[3]), collapse_id=row[0]) for row in cur.fetchall()]
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
        try:
            send_email_to_user(owner)
        except:
            print("Send email failure")

    try:
        return redirect(url_for("column.show_essay"))
    except TemplateNotFound:
        abort(404)

