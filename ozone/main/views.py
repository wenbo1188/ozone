import time
import os

from jinja2 import TemplateNotFound

from flask import abort
from flask import current_app as app
from flask import redirect, render_template, request, session, url_for, flash, send_from_directory

from . import main_page
from ..config import logger
from ..utils.db_util import get_db
from ..utils.form_util import LoginForm
from sqlite3 import DatabaseError


def get_playlist_info() -> tuple:
    """Get playlist info from file under folder: ../songs_rank/"""

    logger.info("Getting playlist info")

    playlist1 = []
    playlist2 = []

    filepath1 = "{}/{}.txt".format(app.config["PLAYLIST_PATH"], app.config["USERNAME1"])
    filepath2 = "{}/{}.txt".format(app.config["PLAYLIST_PATH"], app.config["USERNAME2"])

    if os.path.exists(filepath1) and os.path.isfile(filepath1) and os.path.exists(filepath2) and os.path.isfile(filepath2):
        # Path exists
        with open(filepath1, 'r', encoding="utf-8") as file1:
            lines = file1.readlines()
            song = []
            for i in range(len(lines)):
                if i % 3 == 0:
                    name = lines[i].strip('\n')
                    song.append(name)
                elif i % 3 == 1:
                    id = lines[i].strip('\n')
                    song.append(id)
                elif i % 3 == 2:
                    url = lines[i].strip('\n')
                    song.append(url)
                    playlist1.append(song)
                    song = []

        with open(filepath2, 'r', encoding="utf-8") as file2:
            lines = file2.readlines()
            song = []
            for i in range(len(lines)):
                if i % 3 == 0:
                    name = lines[i].strip('\n')
                    song.append(name)
                elif i % 3 == 1:
                    id = lines[i].strip('\n')
                    song.append(id)
                elif i % 3 == 2:
                    url = lines[i].strip('\n')
                    song.append(url)
                    playlist2.append(song)
                    song = []

    else:
        # path not exists
        create_files_command = "touch {} && touch {}".format(filepath1, filepath2)
        err_code = os.system(create_files_command)
        if err_code != 0:
            logger.error("Fail to create file path: {} and {}".format(filepath1, filepath2))
        else:
            logger.info("Success create file path: {} and {}".format(filepath1, filepath2))

    logger.debug("\nplaylist1: {}\nplaylist2: {}".format(playlist1, playlist2))

    return playlist1, playlist2


def get_exhibition_essay() -> list:
    """Get essay for exhibition in index.html"""

    exhibition_num = 4

    with app.app_context():
        db = get_db()
        try:
            cur = db.cursor().execute("select timestamp, owner, title, content from essay order by timestamp desc limit ?", [exhibition_num,])
        except DatabaseError as err:
            logger.error("Invalid database operation:{}".format(err))
            return []
        exhibition = [dict(timestamp=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(row[0])), owner=row[1], title=row[2], content=row[3], collapse_id=row[0]) for row in cur.fetchall()]

    return exhibition


def get_exhibition_photo() -> list:
    """Get photo for exhibition in index.html"""

    from .. import photos
    exhibition_num = 4

    with app.app_context():
        db = get_db()
        try:
            cur = db.cursor().execute("select distinct name from photo where exhibition = 1 order by last_chosen_time limit ?", [exhibition_num,])
        except DatabaseError as err:
            logger.error("Invalid database operation:{}".format(err))
            return []
        exhibition = [dict(url=photos.url(row["name"])) for row in cur.fetchall()]

    return exhibition


@main_page.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        if username == app.config['USERNAME1'] and password == app.config['PASSWORD']:
            session["logged_in"] = True
            session["logged_user"] = app.config['USERNAME1']
            logger.info("Login as {}".format(app.config['USERNAME1']))
        elif username == app.config['USERNAME2'] and password == app.config['PASSWORD']:
            session["logged_in"] = True
            session["logged_user"] = app.config['USERNAME2']
            logger.info("Login as {}".format(app.config['USERNAME2']))
        else:
            logger.warning("Wrong username or password: {}, {}".format(username, password))
            flash("Wrong username or password", "danger")
            return render_template("login.html", form=form)
        
        flash("You have successfully logged in", "success")
        return redirect(url_for("main.index"))

    return render_template("login.html", form=form)


@main_page.route('/logout')
def logout():
    if "logged_user" not in session:
        flash("You have not logged in yet!", "warning")
        return redirect(url_for("main.index"))
    
    logger.info("{} has logged out".format(session["logged_user"]))

    session.pop("logged_in", None)
    session.pop("logged_user", None)
    flash("You have successfully logged out!", "success")
    return redirect(url_for("main.index"))


@main_page.route('/', methods=['GET'])
def index():
    if "logged_in" in session and session["logged_in"] == True:
        list1, list2 = get_playlist_info() #to be removed
        exhibition = get_exhibition_essay()
        photo_exhibition = get_exhibition_photo()
        logger.info("Index.html visited")
        logger.debug("photo_exhibition: {}".format(photo_exhibition))
        return render_template("index.html", playlist1=list1, playlist2=list2, exhibition=exhibition, photo_exhibition=photo_exhibition)
    else:
        return render_template("index.html")


@main_page.route('/_uploads/photos/<photo_name>')
def get_url(photo_name):
    return send_from_directory(app.config['UPLOADED_PHOTOS_DEST'], photo_name)


@main_page.route('/manage/<string:function>', methods=['GET'])
def manage(function):
    if "logged_in" in session and session["logged_in"] == True:
        with app.app_context():
            db = get_db()
            if session["logged_user"] == app.config["USERNAME1"]:
                owner = "汪先森"
            elif session["logged_user"] == app.config["USERNAME2"]:
                owner = "小笨笨"
            else:
                logger.error("Invalid username, something goes wrong!!!")

            logger.debug("username:{}".format(owner))

            if function == 'message':
                # Get messages
                try:
                    cur = db.cursor().execute("select timestamp, owner, content from message where owner = ? order by timestamp desc", [owner])
                except DatabaseError as err:
                    logger.error("Invalid database operation:{}".format(err))
                    abort(404)
                messages = [dict(timestamp=row[0], owner=row[1], content=row[2]) for row in cur.fetchall()]
                logger.debug("message:\n{}".format(messages))

                return render_template("message_manage.html", messages=messages)
            elif function == 'column':
                # Get essays
                try:
                    cur = db.cursor().execute("select timestamp, owner, title, content from essay where owner = ? order by timestamp desc", [owner])
                except DatabaseError as err:
                    logger.error("Invalid database operation:{}".format(err))
                    abort(404)
                essays = [dict(timestamp=row[0], owner=row[1], title=row[2], content=row[3]) for row in cur.fetchall()]
                logger.debug("essay:\n{}".format(essays))

                return render_template("column_manage.html", essays = essays)
                
            elif function == 'album':
                # Get photos
                try:
                    cur = db.cursor().execute("select id, name, album, timestamp from photo order by timestamp desc")
                except DatabaseError as err:
                    logger.error("Invalid database operation:{}".format(err))
                    abort(404)
                photos = [dict(id=row["id"], name=row["name"], album=row["album"], timestamp=row["timestamp"]) 
                        for row in cur.fetchall()]
                logger.debug("photos:\n{}".format(photos))

                # Get albums
                try:
                    cur = db.cursor().execute("select id, title, about, cover, timestamp from album order by timestamp desc")
                except DatabaseError as err:
                    logger.error("Invalid database operation:{}".format(err))
                    abort(404)
                albums = [dict(id=row["id"], title=row["title"], about=row["about"], cover=row["cover"], timestamp=row["timestamp"])
                        for row in cur.fetchall()]
                logger.debug("albums:\n{}".format(albums))

                return render_template("photo_manage.html", photos=photos, albums=albums)
            else:
                logger.error("Wrong parameter received")
                abort(404)
    else:
        flash("You need login to continue", "warning")
        return redirect(url_for("main.login"))