from wsgiref.simple_server import make_server
from assets import asset

port = 8080

def application(environ, start_response):    
    status = '200 OK'
    headers = [('Content-Type', 'application/octet-stream')]
    start_response(status, headers)

    tokens = environ['PATH_INFO'].split('/')
    lang, platform = tokens[-2].split('-')
    return [asset(lang, platform, tokens[-1])]

with make_server('', port, application) as httpd:
    print(f'Serving HTTP on port {port}...')
    httpd.serve_forever()
