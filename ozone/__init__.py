from flask import Flask, g
from .config import logger
from flask import current_app
from .main import main_page
from .message import message_page
from .column import column_page
from .utils.db_util import get_db
import time

def danger_str_filter(string_to_filter : str):
    '''
    Filter to skip dangerous html tag
    '''

    danger_list = ["<script>", "</script>", "<body>", "</body>"]
    for danger_str in danger_list:
        string_to_filter = string_to_filter.replace(danger_str, "")

    return string_to_filter

def my_truncate(string_to_filter : str, length=255, end="..."):
    '''
    Truncate strings to the given length
    '''

    result = "{}{}".format(string_to_filter[:length], end)
    return result

def my_timefmt(string_to_filter : str):
    '''
    Transform timestamp of integer to certain format
    '''

    result = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(string_to_filter))
    return result

def register_filter():
    '''Register the filter to skip dangerous html tag'''

    logger.info("Registering filter")

    env = current_app.jinja_env
    env.filters['my_str_filter'] = danger_str_filter
    env.filters['my_truncate'] = my_truncate
    env.filters['my_timefmt'] = my_timefmt

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
