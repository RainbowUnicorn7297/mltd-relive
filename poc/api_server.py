from wsgiref.simple_server import make_server
from ssl import SSLContext, PROTOCOL_TLS_SERVER
from handler import application

port = 8443

def start(port):
    with make_server('', port, application) as httpd:
        certfile = '../key/api.crt'
        keyfile = '../key/api.key'
        context = SSLContext(PROTOCOL_TLS_SERVER)
        context.load_cert_chain(certfile, keyfile)
        httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
        # uncomment to debug SSL errors
##        httpd.socket.accept()

        print(f'Serving HTTPS on port {port}...')
        httpd.serve_forever()

if __name__ == "__main__":
    start(port)
