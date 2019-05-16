from ozone import create_app
from ozone.config import ProdConfigLinux, DevConfigLinux, ProdConfigWindows, DevConfigWindows, logger
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from ozone.utils.music_util import query_loop
import threading
import argparse
import platform


def songs_rank_thread(config):
    """Songs rank thread"""

    query_loop(config)


def webserver_thread(app):
    """Ozone app server thread"""

    http_server = HTTPServer(WSGIContainer(app))
    http_server.listen(5000)
    IOLoop.instance().start()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Ozone app parser')
    parser.add_argument("--debug", action="store_true", help="Launch in debug mode")
    args = parser.parse_args()

    # Judge the platform
    platform_info = platform.platform()
    if "Windows" in platform_info:
        if args.debug:
            app = create_app(DevConfigWindows)
            song_thread = threading.Thread(target=songs_rank_thread, args=(DevConfigWindows,))
        else:
            app = create_app(ProdConfigWindows)
            song_thread = threading.Thread(target=songs_rank_thread, args=(ProdConfigWindows,))
    elif "Linux" in platform_info:
        if args.debug:
            app = create_app(DevConfigLinux)
            song_thread = threading.Thread(target=songs_rank_thread, args=(DevConfigLinux,))
        else:
            app = create_app(ProdConfigLinux)
            song_thread = threading.Thread(target=songs_rank_thread, args=(ProdConfigLinux,))
    else:
        logger.warning("Unrecognized platform, assuming it works fine with linux platform")
        if args.debug:
            app = create_app(DevConfigLinux)
            song_thread = threading.Thread(target=songs_rank_thread, args=(DevConfigLinux,))
        else:
            app = create_app(ProdConfigLinux)
            song_thread = threading.Thread(target=songs_rank_thread, args=(ProdConfigLinux,))

    song_thread.start()
    
    if app.config['DEBUG']:
        logger.info("Launch in debug mode")
        app.run(debug=True)
    else:
        logger.info("Launch in normal mode")
        webserver_thread(app)