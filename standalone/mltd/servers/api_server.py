import socket
import sys
from os import path
from wsgiref.simple_server import WSGIRequestHandler, make_server

from mltd.servers.config import api_port
from mltd.servers.handler import application
from mltd.servers.logging import logger


# A hack to prevent slow http.server.HTTPServer startup time on Windows.
# When a new HTTPServer object is created, it calls socket.getfqdn('')
# to get the fully qualified domain name of the device this Python
# program is running on. Since this program is expected to only run on
# PCs and phones, the hostname returned by the OS usually cannot be
# resolved by the DNS. DNS lookup failures are especially bad on Windows
# due to its long default timeout.
def bare_getfqdn(name=''):
    return ''
socket.getfqdn = bare_getfqdn


class SilentWSGIRequestHandler(WSGIRequestHandler):

    def log_message(self, format, *args):
        # Disable stderr output
        pass


def key_path():
    base_path = getattr(sys, '_MEIPASS', path.abspath('..'))
    return path.join(base_path, 'key')


def start(port=api_port, conn=None):
    with make_server('', port, application,
                     handler_class=SilentWSGIRequestHandler) as httpd:
        logger.info(f'Serving HTTP on port {port}...')
        if conn:
            conn.send(True)
            conn.close()
        httpd.serve_forever()


if __name__ == '__main__':
    start()

