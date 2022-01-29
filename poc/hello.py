def application(environ, start_response):
    status = '200 OK'
    headers = [('Content-Type', 'text/html')]
    
    start_response(status, headers)

    print('\n'.join([str(('%s: %s' % (key, value)).encode('utf-8'))
                     for key, value in environ.items()]))
    return [b'<h1>Hello, web!</h1>']
