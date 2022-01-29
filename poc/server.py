from wsgiref.simple_server import make_server
from hello import application

with make_server('', 443, application) as httpd:
    print('Serving HTTP on port 443...')
    httpd.serve_forever()
