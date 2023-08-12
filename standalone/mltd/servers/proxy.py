import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from os import path
from ssl import PROTOCOL_TLS_SERVER, SSLContext

import requests
import urllib3

from mltd.servers.logging import logger

_proxy_port = 443
_api_port = 8443

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class ProxyHTTPRequestHandler(BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'
    close_connection = True

    def do_POST(self):
        host = 'localhost:' + str(_api_port)
        url = f'https://{host}{self.path}'
        content_len = int(self.headers.get('Content-Length'))
        req_body = self.rfile.read(content_len)

        incomplete = True
        while incomplete:
            resp = requests.post(url, headers=self.headers, data=req_body,
                                 stream=True, verify=False)
            content_len = int(resp.headers['Content-Length'])
            content = resp.raw.read(content_len)
            if len(content) == content_len:
                incomplete = False

        self.send_response(resp.status_code)
        for h in resp.headers:
            if h not in ['Server', 'Date']:
                self.send_header(h, resp.headers[h])
        self.send_header('Connection', 'close')
        self.end_headers()
        self.wfile.write(content)


def key_path():
    base_path = getattr(sys, '_MEIPASS', path.abspath('..'))
    return path.join(base_path, 'key')


def start(port):
    server_address = ('', port)
    httpd = HTTPServer(server_address, ProxyHTTPRequestHandler)
    certfile = path.join(key_path(), 'api.crt')
    keyfile = path.join(key_path(), 'api.key')
    context = SSLContext(PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile, keyfile)
    httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
    # Uncomment next line to debug SSL errors
    # httpd.socket.accept()

    logger.info(f'Reverse proxy is running on port {port}...')
    httpd.serve_forever()


if __name__ == '__main__':
    start(_proxy_port)

