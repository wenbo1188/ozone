import sqlite3
import time

from jinja2 import TemplateNotFound

from flask import Blueprint, abort
from flask import current_app as app
from flask import g, redirect, render_template, request, session, url_for, flash

from . import column_page
from ..config import logger
from ..utils.db_util import get_db
from ..utils.reminder_util import EmailReminder
from ..utils.form_util import EssayForm

@column_page.route('/<title>/<int:page>')
def show_essay(title, page=1):
    if "logged_in" not in session:
        flash("You need login to continue", "warning")
        return redirect(url_for("main.login"))

    with app.app_context():
        db = get_db()
        num_per_page = app.config['COLUMN_PER_PAGE']
        # get all the titles
        try:
            cur = db.cursor().execute("select distinct title from essay order by timestamp desc")
        except sqlite3.DatabaseError as err:
            logger.error("Invalid database operation:{}".format(err))
            abort(404)
        titles = [row[0] for row in cur.fetchall()]
        logger.debug("All the titles:\n{}".format(titles))

        if (title == "all"):
            logger.debug("Title is all")

            # get total num of essays
            try:
                cur = db.cursor().execute("select count(*) from essay")
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
                cur = db.cursor().execute("select timestamp, owner, title, content from essay order by timestamp desc limit ? offset ?", [num_per_page, (page - 1) * num_per_page])
            except sqlite3.DatabaseError as err:
                logger.error("Invalid database operation:{}".format(err))
                abort(404)
            essays = [dict(timestamp=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(row[0])), owner=row[1], title=row[2], content=row[3], collapse_id=row[0]) for row in cur.fetchall()]
            logger.debug("Essays:\n{}".format(essays))
        else:
            logger.debug("Title is {}".format(title))
            try:
                cur = db.cursor().execute("select count(*) from essay where title = ?", [title])
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
                cur = db.cursor().execute("select timestamp, owner, title, content from essay where essay.title = ? order by timestamp desc limit ? offset ?", [title, num_per_page, (page - 1) * num_per_page])
            except sqlite3.DatabaseError as err:
                logger.error("Invalid database operation:{}".format(err))
                abort(404)
            essays = [dict(timestamp=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(row[0])), owner=row[1], title=row[2], content=row[3], collapse_id=row[0]) for row in cur.fetchall()]
            logger.debug("Essays:\n{}".format(essays))
        try:
            return render_template("show_essay.html", essays=essays, total_page=max_page, current_page=page, titles=titles, current_title=title)
        except TemplateNotFound:
            logger.error("Template not found")
            abort(404)

@column_page.route('/add', methods=['GET', 'POST'])
def add_essay():
    owner = None
    form = EssayForm()

    # check if log in
    if "logged_in" not in session:
        flash("You need login to continue", "warning")
        return redirect(url_for("main.login"))

    if form.validate_on_submit():
        # start add message
        with app.app_context():
            db = get_db()
            timestamp = int(time.time())
            if session["logged_user"] == "wang":
                owner = "汪先森"
            elif session["logged_user"] == "miao":
                owner = "小笨笨"
            else:
                logger.error("Invalid username, something goes wrong!!!")

            logger.debug("Added title is:\n{}\nContent is:\n{}".format(request.form["title"], request.form["content"]))

            try:
                db.cursor().execute("insert into essay (timestamp, owner, title, content, user1_read, user2_read) values (?, ?, ?, ?, 0, 0)", [timestamp, owner, request.form["title"], request.form["content"]])
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
            message_content = "An essay has been updated, go and have a look~"

            reminder = EmailReminder(app.config['MAIL_SERVER'], app.config['MAIL_PORT'], app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'], False, logger)
            try:
                reminder.send(receiver, receiver_name, message_content)
            except:
                logger.warning("Send email failure")

        try:
            flash("You have successfully add an essay", "success")
            return redirect(url_for("column.show_essay", title="all", page=1))
        except TemplateNotFound:
            logger.error("Template not found")
            abort(404)
    else:
        return render_template("add_essay.html", form=form)

@column_page.route('/update/<int:timestamp>', methods=['GET', 'POST'])
def update(timestamp):
    # check if log in
    if "logged_in" not in session:
        flash("You need login to continue", "warning")
        return redirect(url_for("main.login"))

    form = EssayForm()

    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        logger.info("Editing essay with timestamp {}".format(timestamp))
        logger.info("New title:\n{}\nNew content:\n{}".format(title, content))

        with app.app_context():
            db = get_db()
            timestamp_new = int(time.time())

            try:
                db.cursor().execute("update essay set timestamp = ?, title = ?, content = ? where timestamp = ?", [timestamp_new, title, content, timestamp])
            except sqlite3.DatabaseError as err:
                logger.error("Invalid database operation:{}".format(err))
                abort(404)
            db.commit()
            logger.info("Success update essay")

            try:
                flash("You have successfully update an essay", "success")
                return redirect(url_for("main.manage", function="column"))
            except TemplateNotFound:
                logger.error("Template not found")
                abort(404)
    else:
        with app.app_context():
            db = get_db()
            try:
                cur = db.cursor().execute("select title, content from essay where timestamp = ?", [timestamp])
            except sqlite3.DatabaseError as err:
                logger.error("Invalid database operation:{}".format(err))
                abort(404)
            result = cur.fetchone()
            old_essay = dict(title=result[0], content=result[1])
            logger.debug("{}".format(old_essay))
        
            return render_template("update.html", form=form, old_essay=old_essay, timestamp=timestamp)

@column_page.route('/delete/<int:timestamp>', methods=['GET'])
def delete(timestamp):
    #check if log in
    if "logged_in" not in session:
        flash("You need login to continue", "warning")
        return redirect(url_for("main.login"))
    
    with app.app_context():
        db = get_db()
        try:
            db.cursor().execute("delete from essay where timestamp = ?", [timestamp])
        except sqlite3.DatabaseError as err:
            logger.error("Invalid database operation:{}".format(err))
            abort(404)
        db.commit()
        logger.info("Success delete essay")

        flash("You have successfully delete an essay", "success")
        return redirect((url_for('main.manage', function="column")))