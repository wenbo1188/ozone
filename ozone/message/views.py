import sqlite3
import time

from jinja2 import TemplateNotFound

from flask import abort
from flask import current_app as app
from flask import g, redirect, render_template, request, session, url_for, flash

from . import message_page
from ..config import logger
from ..utils.db_util import get_db
from ..utils.reminder_util import EmailReminder
from ..utils.form_util import MessageForm

@message_page.route('/<int:page>')
def show_message(page=1):
    if "logged_in" not in session:
        flash("You need login to continue", "warning")
        return redirect(url_for("main.login"))

    with app.app_context():
        db = get_db()
        num_per_page = app.config['MESSAGE_PER_PAGE']

        # get total num of messages
        try:
            cur = db.cursor().execute("select count(*) from message")
        except sqlite3.DatabaseError as err:
            logger.error("Invalid database operation:{}".format(err))
            abort(404)
        num = cur.fetchall()[0][0]
        if (num % num_per_page == 0):
            max_page = int(num / num_per_page)
        else:
            max_page = int((num / num_per_page) + 1)

        logger.debug("Total num of message is {}, max_page is {}".format(num, max_page))
        
        if ((page - 1) * num_per_page >= num):
            logger.warning("Illegal page number: {}".format(page))
            page = max_page

        if (page <= 0):
            logger.warning("Illegal page number: {}".format(page))
            page = 1

        try:
            cur = db.cursor().execute("select timestamp, owner, content from message order by timestamp desc limit ? offset ?", [num_per_page, (page - 1) * num_per_page])
        except sqlite3.DatabaseError as err:
            logger.error("Invalid database operation:{}".format(err))
            abort(404)
        messages = [dict(timestamp=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(row[0])), owner=row[1], content=row[2]) for row in cur.fetchall()]
        logger.debug("Messages are:\n{}".format(messages))
        try:
            return render_template("show_message.html", messages=messages, total_page=max_page, current_page=page)
        except TemplateNotFound:
            logger.error("Template not found")
            abort(404)

@message_page.route('/add', methods=['GET', 'POST'])
def add_message():
    owner = None
    form = MessageForm()

    # check if log in
    if "logged_in" not in session:
        flash("You need login to continue", "warning")
        return redirect(url_for("main.login"))

    if form.validate_on_submit():
        content = form.content.data
        # start add message
        with app.app_context():
            db = get_db()
            timestamp = int(time.time())
            if session["logged_user"] == app.config['USERNAME1']:
                owner = "汪先森"
            elif session["logged_user"] == app.config['USERNAME2']:
                owner = "小笨笨"
            else:
                logger.error("Invalid username, something goes wrong!!!")
            try:
                db.cursor().execute("insert into message (timestamp, owner, content) values (?, ?, ?)", [timestamp, owner, content])
            except sqlite3.DatabaseError as err:
                logger.error("Invalid database operation:{}".format(err))
                abort(404)
            db.commit()

            # email reminder
            if (owner == "汪先森"):
                receiver = app.config['USER2_MAILADDRESS']
                receiver_name = app.config['USERNAME2']
            elif (owner == "小笨笨"):
                receiver = app.config['USER1_MAILADDRESS']
                receiver_name = app.config['USERNAME1']
            else:
                logger.error("Invalid username, something goes wrong!!!")

            message_content = "A new message for you, go and have a look~"
            reminder = EmailReminder(app.config['MAIL_SERVER'], app.config['MAIL_PORT'], app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'], False, logger)
            try:
                reminder.send(receiver, receiver_name, message_content)
            except:
                logger.warning("Send email failure")

            try:
                flash("You have successfully leave a message", "success")
                return redirect(url_for("message.show_message", page=1))
            except TemplateNotFound:
                logger.error("Template not found")
                abort(404)
    else:
        return render_template('add_message.html', form=form)

@message_page.route('/update/<int:timestamp>', methods=['GET', 'POST'])
def update(timestamp):
    # check if log in
    if "logged_in" not in session:
        flash("You need login to continue", "warning")
        return redirect(url_for("main.login"))

    form = MessageForm()

    if form.validate_on_submit():
        content = form.content.data
        logger.info("Editing message content with timestamp {}".format(timestamp))
        logger.info("New content:\n{}".format(content))

        with app.app_context():
            db = get_db()
            timestamp_new = int(time.time())

            try:
                db.cursor().execute("update message set timestamp = ?, content = ? where timestamp = ?", [timestamp_new, content, timestamp])
            except sqlite3.DatabaseError as err:
                logger.error("Invalid database operation:{}".format(err))
                abort(404)
            db.commit()
            logger.info("Success update message")

            try:
                flash("You have successfully udpate a message", "success")
                return redirect(url_for("main.manage", function="message"))
            except TemplateNotFound:
                logger.error("Template not found")
                abort(404)
    else:
        with app.app_context():
            db = get_db()
            try:
                cur = db.cursor().execute("select content from message where timestamp = ?", [timestamp])
            except sqlite3.DatabaseError as err:
                logger.error("Invalid database operation:{}".format(err))
                abort(404)
            old_message = dict(content=cur.fetchone()[0])
            logger.debug("{}".format(old_message))
        
            return render_template("update.html", form=form, old_message=old_message, timestamp=timestamp)

@message_page.route('/delete/<int:timestamp>', methods=['GET'])
def delete(timestamp):
    #check if log in
    if "logged_in" not in session:
        flash("You need login to continue", "warning")
        return redirect(url_for("main.login"))
    
    with app.app_context():
        db = get_db()
        try:
            db.cursor().execute("delete from message where timestamp = ?", [timestamp])
        except sqlite3.DatabaseError as err:
            logger.error("Invalid database operation:{}".format(err))
            abort(404)
        db.commit()
        logger.info("Success delete message")

        flash("You have successfully delete a message", "success")
        return redirect((url_for('main.manage', function="message")))