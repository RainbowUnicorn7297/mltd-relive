from os import listdir
from assets import asset
import random

def application(environ, start_response):
##    print('\n'.join([str(('%s: %s' % (key, value)).encode('utf-8'))
##                     for key, value in environ.items()]))

    host = environ['HTTP_HOST']

    if host == 'theaterdays-zh.appspot.com' or \
       host == 'theaterdays-ko.appspot.com':
        status = '200 OK'
        headers = [('Content-Type', 'application/json'),
                   ('X-Encryption', 'on'),
                   ('X-Encryption-Compress', 'gzip'),
                   ('X-Encryption-Mode', '3')]
##                   ('X-Server-Date', '2022-02-01T20:00:00+0000')]
        start_response(status, headers)
        
        service = environ['PATH_INFO'].split('/')[-1]
        if service == 'LiveService.GetRandomGuestList':
            responses = [r for r in listdir('responses') if service in r]
            ret = b''
            with open('responses/' + random.choice(responses), 'rb') as f:
                ret = f.read()
            return [ret]
        else:
            ret = b''
            with open('responses/' + service + '.response', 'rb') as f:
                ret = f.read()
            return [ret]
        
    else:
        status = '503 Service Unavailable'
        headers = [('Content-Type', 'text/html')]
        start_response(status, headers)

        return [b'503 Service Unavailable']
