from wsgiref.simple_server import make_server
from hello import application

httpd = make_server('', 443, application)
print('Serving HTTP on port 443...')
httpd.serve_forever()
