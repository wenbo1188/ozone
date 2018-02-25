from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from message import message_page
import sqlite3
import os
from config import ProdConfig

app = Flask(__name__)
app.config.from_object(ProdConfig)
app.register_blueprint(message_page, url_prefix="/message")

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
            db.cursor().executescript(f.read())
        db.commit()
        print("success init db")

if __name__ == '__main__':
    init_db()
    app.run()
