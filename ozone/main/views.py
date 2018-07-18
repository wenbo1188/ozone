from flask import render_template, request, session, redirect, url_for, abort
from flask import current_app as app
from jinja2 import TemplateNotFound
from ..config import logger
from . import main_page
from ..utils.form_util import LoginForm

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
            return render_template("login.html")
        return redirect(url_for("main.index"))

    return render_template("login.html", form=form)

@main_page.route('/logout')
def logout():
    logger.info("{} has logged out".format(session["logged_user"]))

    session.pop("logged_in", None)
    return redirect(url_for("main.index"))

@main_page.route('/', methods=['GET'])
def index():
    logger.info("Index.html visited")

    if "logged_in" in session and session["logged_in"] == True:
        list1, list2 = get_playlist_info() #to be removed
        return render_template("index.html", playlist1=list1, playlist2=list2)
    else:
        return render_template("index.html")
