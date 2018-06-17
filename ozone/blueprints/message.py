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

def send_async_email(msg, mail_username, mail_password, mail_server, to_addr, debug = False):
    server = smtplib.SMTP(mail_server, 25)
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

    #message_content = owner + "更新了专题，快去看看吧~"
    message_content = "A new message for you, go and have a look~"
    message = MIMEText(message_content, 'text', 'utf-8')
    message['Subject'] = Header("Ozone消息提醒", 'utf-8')
    message['From'] = 'Ozone消息管家<13188316906@163.com>'
    message['To'] = receiver_name + '<' + receiver + '>'

    mail_thread = threading.Thread(target = send_async_email, args = [message, mail_username, mail_password, mail_server, receiver])
    mail_thread.start()
    #mail.send(message)
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

