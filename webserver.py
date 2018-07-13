from ozone import create_app
from config import ProdConfig
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

if __name__ == '__main__':
    app = create_app(ProdConfig)
    http_server = HTTPServer(WSGIContainer(app))
    http_server.listen(5000)
    IOLoop.instance().start()
    
