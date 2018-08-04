import time

from jinja2 import TemplateNotFound

from flask import abort
from flask import current_app as app
from flask import redirect, render_template, request, session, url_for, flash

from . import main_page
from ..config import logger
from ..utils.db_util import get_db
from ..utils.form_util import LoginForm
from sqlite3 import DatabaseError


def get_playlist_info() -> tuple:
    '''
    get playlist info from file under folder: ../songs_rank/
    '''

    logger.info("Getting playlist info")

    playlist1 = []
    playlist2 = []

    filepath1 = "{}/{}.txt".format(app.config["PLAYLIST_PATH"], app.config["USERNAME1"])
    filepath2 = "{}/{}.txt".format(app.config["PLAYLIST_PATH"], app.config["USERNAME2"])

    with open(filepath1, 'r') as file1:
        try:
            line = file1.readline()
        except:
            logger.error("Fail to read oneline")

        while line:
            name = line.strip('\n')
            song = []
            song.append(name)
            try:
                line = file1.readline()
            except:
                logger.error("Fail to read oneline")
            id = line.strip('\n')
            song.append(id)
            try:
                line = file1.readline()
            except:
                logger.error("Fail to read oneline")
            url = line.strip('\n')
            song.append(url)
            playlist1.append(song)
            try:
                line = file1.readline()
            except:
                logger.error("Fail to read oneline")

    with open(filepath2, 'r') as file2:
        try:
            line = file2.readline()
        except:
            logger.error("Fail to read oneline")

        while line:
            name = line.strip('\n')
            song = []
            song.append(name)
            try:
                line = file2.readline()
            except:
                logger.error("Fail to read oneline")
            id = line.strip('\n')
            song.append(id)
            try:
                line = file2.readline()
            except:
                logger.error("Fail to read oneline")
            url = line.strip('\n')
            song.append(url)
            playlist2.append(song)
            try:
                line = file2.readline()
            except:
                logger.error("Fail to read oneline")

    file1.close()
    file2.close()

    logger.debug("\nplaylist1: {}\nplaylist2: {}".format(playlist1, playlist2))

    return playlist1, playlist2

def get_exhibition_essay() -> list:
    '''
    Get essay for exhibition in index.html
    '''

    exhibition_num = 4

    with app.app_context():
        db = get_db()
        try:
            cur = db.cursor().execute("select timestamp, owner, title, content from essay order by timestamp desc limit ?", [exhibition_num])
        except DatabaseError as err:
            logger.error("Invalid database operation:{}".format(err))
            return []
        exhibition = [dict(timestamp=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(row[0])), owner=row[1], title=row[2], content=row[3], collapse_id=row[0]) for row in cur.fetchall()]

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
            return render_template("login.html")
        
        flash("You have successfully logged in", "success")
        return redirect(url_for("main.index"))

    return render_template("login.html", form=form)

@main_page.route('/logout')
def logout():
    logger.info("{} has logged out".format(session["logged_user"]))

    session.pop("logged_in", None)
    flash("You have successfully logged out!", "success")
    return redirect(url_for("main.index"))

@main_page.route('/', methods=['GET'])
def index():
    logger.info("Index.html visited")

    if "logged_in" in session and session["logged_in"] == True:
        list1, list2 = get_playlist_info() #to be removed
        exhibition = get_exhibition_essay()
        return render_template("index.html", playlist1=list1, playlist2=list2, exhibition=exhibition)
    else:
        return render_template("index.html")

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
                # get messages
                try:
                    cur = db.cursor().execute("select timestamp, owner, content from message where owner = ? order by timestamp desc", [owner])
                except DatabaseError as err:
                    logger.error("Invalid database operation:{}".format(err))
                    abort(404)
                messages = [dict(timestamp=row[0], owner=row[1], content=row[2]) for row in cur.fetchall()]
                logger.debug("message:\n{}".format(messages))

                return render_template("message_manage.html", messages=messages)
            elif function == 'column':
                # get essays
                try:
                    cur = db.cursor().execute("select timestamp, owner, title, content from essay where owner = ? order by timestamp desc", [owner])
                except DatabaseError as err:
                    logger.error("Invalid database operation:{}".format(err))
                    abort(404)
                essays = [dict(timestamp=row[0], owner=row[1], title=row[2], content=row[3]) for row in cur.fetchall()]
                logger.debug("essay:\n{}".format(essays))

                return render_template("column_manage.html", essays = essays)
                
            elif function == 'album':
                # get photos
                try:
                    cur = db.cursor().execute("select id, name, album, timestamp from photo order by timestamp desc")
                except DatabaseError as err:
                    logger.error("Invalid database operation:{}".format(err))
                    abort(404)
                photos = [dict(id=row["id"], name=row["name"], album=row["album"], timestamp=row["timestamp"]) for row in cur.fetchall()]
                logger.debug("photo:\n{}".format(photos))

                return render_template("photo_manage.html", photos=photos)
            else:
                logger.error("Wrong parameter received")
                abort(404)
    else:
        flash("You need login to continue", "warning")
        return redirect(url_for("main.login"))