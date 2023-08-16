import sys
from os import path
from ssl import PROTOCOL_TLS_SERVER, SSLContext
from wsgiref.simple_server import WSGIRequestHandler, make_server

from mltd.servers.handler import application
from mltd.servers.logging import logger

api_port = 8443


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
        certfile = path.join(key_path(), 'api.crt')
        keyfile = path.join(key_path(), 'api.key')
        context = SSLContext(PROTOCOL_TLS_SERVER)
        context.load_cert_chain(certfile, keyfile)
        httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
        # Uncomment next line to debug SSL errors
        # httpd.socket.accept()

        logger.info(f'Serving HTTPS on port {port}...')
        httpd.serve_forever()


if __name__ == '__main__':
    start()

