from ozone import create_app
from ozone.config import ProdConfig, DevConfig, logger
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from ozone.utils.music_util import query_loop
import threading
import argparse

def songs_rank_thread():
    '''
    Songs rank thread
    '''

    query_loop()

def webserver_thread(app):
    '''
    Ozone app server thread
    '''

    http_server = HTTPServer(WSGIContainer(app))
    http_server.listen(5000)
    IOLoop.instance().start()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Ozone app parser')
    parser.add_argument("--debug", action="store_true", help="Launch in debug mode")
    args = parser.parse_args()
    if args.debug:
        app = create_app(DevConfig)
    else:
        app = create_app(ProdConfig)

    song_thread = threading.Thread(target=songs_rank_thread)
    song_thread.start()
    
    if app.config['DEBUG']:
        logger.info("Launch in debug mode")
        app.run(debug=True)
    else:
        logger.info("Launch in normal mode")
        webserver_thread(app)