from wsgiref.simple_server import make_server
from ssl import SSLContext, PROTOCOL_TLS_SERVER
from handler import application

with make_server('', 443, application) as httpd:
    certfile = '../key/api.crt'
    keyfile = '../key/api.key'
    context = SSLContext(PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile, keyfile)
##    httpd.socket = wrap_socket(
##        httpd.socket, certfile=certfile, keyfile=keyfile, server_side=True)
    httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
##    httpd.socket.accept()
    
    print('Serving HTTPS on port 443...')
    httpd.serve_forever()
