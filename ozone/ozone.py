from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from message import message_page
from column import column_page
import sqlite3
import os
from config import ProdConfig

app = Flask(__name__)
app.config.from_object(ProdConfig)
app.register_blueprint(message_page, url_prefix="/message")
app.register_blueprint(column_page, url_prefix="/column")

def get_playlist_info():
    '''
    get playlist info from file under folder: ../songs_rank/
    '''

    playlist1 = []
    playlist2 = []

    filepath1 = "../songs_rank/{}.txt".format(app.config["USERNAME1"])
    filepath2 = "../songs_rank/{}.txt".format(app.config["USERNAME2"])

    with open(filepath1, 'r') as file1:
        try:
            line = file1.readline()
        except:
            print("fail to read oneline")

        while line:
            line = line.strip('\n')
            playlist1.append(line)
            try:
                line = file1.readline()
            except:
                print("fail to read oneline")

    with open(filepath2, 'r') as file2:
        try:
            line = file2.readline()
        except:
            print("fail to read oneline")

        while line:
            line = line.strip('\n')
            playlist2.append(line)
            try:
                line = file2.readline()
            except:
                print("fail to read oneline")

    file1.close()
    file2.close()

    # print(playlist1, playlist2)
    return playlist1, playlist2

def connect_db():
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource("schema.sql", mode='r') as f:
            try:
                db.cursor().executescript(f.read())
                db.commit()
                # print("success init db")
            except: 
                print("fail to init db")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form["username"] == app.config['USERNAME1'] and request.form["password"] == app.config['PASSWORD']:
            session["logged_in"] = True
            session["logged_user"] = app.config['USERNAME1']
        elif request.form["username"] == app.config['USERNAME2'] and request.form["password"] == app.config['PASSWORD']:
            session["logged_in"] = True
            session["logged_user"] = app.config['USERNAME2']
        else:
            return render_template("login.html")
        # print("%s have logged in" % request.form["username"])
        return redirect(url_for("index"))
    return render_template("login.html")

@app.route('/logout')
def logout():
    session.pop("logged_in", None)
    # print("%s have logged out" % session["logged_user"])
    return redirect(url_for("index"))

@app.route('/', methods=['GET'])
def index():
    # print("index visit")
    list1, list2 = get_playlist_info()
    return render_template("index.html", playlist1=list1, playlist2=list2)

if __name__ == '__main__':
    init_db()
    app.run(host="0.0.0.0")
