from flask import Flask, g
from config import logger
from flask import current_app
from main import main_page
from blueprints.message import message_page
from column import column_page
import sqlite3

def danger_str_filter(string_to_filter : str):
    '''filter to skip dangerous html tag'''

    danger_list = ["<script>", "</script>", "<body>", "</body>"]
    for danger_str in danger_list:
        string_to_filter = string_to_filter.replace(danger_str, "")

    return string_to_filter

def register_filter():
    '''Register the filter to skip dangerous html tag'''

    logger.info("Registering filter")

    env = current_app.jinja_env
    env.filters['my_str_filter'] = danger_str_filter

def connect_db():
    logger.info("Connect to database...")
    
    rv = sqlite3.connect(current_app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
        return g.sqlite_db

def init_db():
    logger.info("Initializing database...")

    db = get_db()
    with current_app.open_resource("schema.sql", mode='r') as f:
        try:
            db.cursor().executescript(f.read())
            db.commit()
            logger.info("Success to init db")
        except:
            logger.error("Fail to init db")
        # finally:
            # close_db()

def create_app(config):
    '''Initializing app'''

    app = Flask(__name__)
    app.config.from_object(config)
    app.register_blueprint(main_page)
    app.register_blueprint(message_page, url_prefix="/message")
    app.register_blueprint(column_page, url_prefix="/column")
    with app.app_context():
        register_filter()
        init_db()
    
        @current_app.teardown_appcontext
        def close_db(error):
            if hasattr(g, 'sqlite_db'):
                logger.info("Closing database...")
                g.sqlite_db.close()

    return app
