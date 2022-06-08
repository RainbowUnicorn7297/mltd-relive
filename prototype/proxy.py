from http.server import BaseHTTPRequestHandler, HTTPServer
from ssl import SSLContext, PROTOCOL_TLS_SERVER
from os import path
import sys, requests
import urllib3

port = 443
api_port = 8443

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class ProxyHTTPRequestHandler(BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'
    close_connection = True

    def do_POST(self):
        host = 'localhost:' + str(api_port)
        url = f'https://{host}{self.path}'
        content_len = int(self.headers.get('Content-Length'))
        req_body = self.rfile.read(content_len)

        incomplete = True
        while incomplete:
            resp = requests.post(url, headers=self.headers,
                                 data=req_body, verify=False)
            content_len = resp.headers['Content-Length']
            if len(resp.content) == int(content_len):
                incomplete = False

        self.send_response(resp.status_code)
        for h in resp.headers:
            if h not in ['Server', 'Date']:
                self.send_header(h, resp.headers[h])
        self.send_header('Connection', 'close')
        self.end_headers()
        self.wfile.write(resp.content)

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
    # uncomment to debug SSL errors
##    httpd.socket.accept()

    print(f'Reverse proxy is running on port {port}...')
    httpd.serve_forever()

if __name__ == '__main__':
    start(port)
