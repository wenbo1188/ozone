from ozone import create_app
from config import ProdConfig
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from songs_rank.songs_rank import query_loop
import threading

def songs_rank_thread():
    query_loop()

def webserver_thread(app):
    http_server = HTTPServer(WSGIContainer(app))
    http_server.listen(5000)
    IOLoop.instance().start()

if __name__ == '__main__':
    app = create_app(ProdConfig)
    song_thread = threading.Thread(target=songs_rank_thread)
    song_thread.start()
    webserver_thread(app)