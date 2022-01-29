from wsgiref.simple_server import make_server
from ssl import wrap_socket
from hello import application

with make_server('', 443, application) as httpd:
    certfile = '../key/server.crt'
    keyfile = '../key/server.key'
    httpd.socket = wrap_socket(
        httpd.socket, certfile=certfile, keyfile=keyfile, server_side=True)
    httpd.socket.accept()
    
    print('Serving HTTPS on port 443...')
    httpd.serve_forever()
