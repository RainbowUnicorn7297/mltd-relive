import sys
from os import path
from ssl import PROTOCOL_TLS_SERVER, SSLContext
from wsgiref.simple_server import WSGIRequestHandler, make_server

from mltd.servers.config import api_port
from mltd.servers.handler import application
from mltd.servers.logging import logger


class SilentWSGIRequestHandler(WSGIRequestHandler):

    def log_message(self, format, *args):
        # Disable stderr output
        pass


def key_path():
    base_path = getattr(sys, '_MEIPASS', path.abspath('..'))
    return path.join(base_path, 'key')


def start(port=api_port):
    with make_server('', port, application,
                     handler_class=SilentWSGIRequestHandler) as httpd:
        logger.info(f'Serving HTTP on port {port}...')
        httpd.serve_forever()


if __name__ == '__main__':
    start()

