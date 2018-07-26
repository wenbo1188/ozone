import sqlite3

from flask import current_app, g

from ..config import logger


def connect_db():
    logger.info("Connect to database...")
    
    rv = sqlite3.connect(current_app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
        return g.sqlite_db