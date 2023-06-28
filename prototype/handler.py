import random
import sys
from os import listdir, path

from encryption import decrypt_request


def response_path():
    base_path = getattr(sys, '_MEIPASS', path.abspath('.'))
    return path.join(base_path, 'responses')


def application(environ, start_response):
    # print('\n'.join([str((f'{key}: {value}').encode('utf-8'))
    #                  for key, value in environ.items()]))

    host = environ['HTTP_HOST']

    if ('theaterdays-zh.appspot.com' in host
            or 'theaterdays-ko.appspot.com' in host):
        status = '200 OK'
        headers = [
            ('Content-Type', 'application/json'),
            ('X-Encryption', 'on'),
            ('X-Encryption-Compress', 'gzip'),
            ('X-Encryption-Mode', '3'),
            # ('X-Server-Date', '2022-02-01T20:00:00+0000'),
        ]

        service = environ['PATH_INFO'].split('/')[-1]
        response = service + '.response'
        if service == 'AssetService.GetAssetVersion':
            lang = 'zh' if 'theaterdays-zh.appspot.com' in host else 'ko'
            platform = environ['HTTP_X_OS_NAME']
            if platform != 'android':
                platform = 'ios'
            response = f'{service}.response.{lang}-{platform}'
        elif service == 'LiveService.GetRandomGuestList':
            responses = [r for r in listdir(response_path()) if service in r]
            response = random.choice(responses)
        elif service == 'EventService.GetEventTalkStoryDetail':
            request_len = int(environ['CONTENT_LENGTH'])
            request = environ['wsgi.input'].read(request_len)
            request = decrypt_request(request)
            story_id = request['params'][0]['event_talk_story_id']
            response = f'{service}.response.{story_id}'
        elif service == 'BatchReqest_MakeCache':
            request_len = int(environ['CONTENT_LENGTH'])
            request = environ['wsgi.input'].read(request_len)
            request = decrypt_request(request)
            if len(request) == 1:
                response = f'{request[0]["method"]}.response'
        response = path.join(response_path(), response)

        ret = b''
        with open(response, 'rb') as f:
            ret = f.read()
        start_response(status, headers)
        return [ret]

    else:
        status = '503 Service Unavailable'
        headers = [('Content-Type', 'text/html')]
        start_response(status, headers)
        return [b'503 Service Unavailable']

