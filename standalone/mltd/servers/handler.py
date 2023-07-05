import json
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from jsonrpc import JSONRPCResponseManager, dispatcher

from mltd.servers.encryption import decrypt_request, encrypt_response
from mltd.servers.utilities import format_datetime
from mltd.services import *


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, UUID):
            return str(o)
        elif isinstance(o, Decimal):
            return float(o.normalize())
        elif isinstance(o, datetime):
            return format_datetime(o)
        return json.JSONEncoder.default(self, o)


def application(environ, start_response):
    host = environ['HTTP_HOST']

    if ('theaterdays-zh.appspot.com' in host
            or 'theaterdays-ko.appspot.com' in host
            or 'localhost' in host):    # For debugging
        status = '200 OK'
        headers = [
            ('Content-Type', 'application/json'),
            ('X-Encryption', 'on'),
            ('X-Encryption-Compress', 'gzip'),
            ('X-Encryption-Mode', '3'),
            # ('X-Server-Date', '2022-02-01T20:00:00+0000'),
        ]

        request_len = int(environ['CONTENT_LENGTH'])
        request = environ['wsgi.input'].read(request_len)
        print(request)  # For debugging
        request = decrypt_request(request)

        context = {
            'user_id': environ.get('HTTP_X_APPLICATION_USER_ID'),
        }
        response = JSONRPCResponseManager.handle(request, dispatcher, context)
        if environ['PATH_INFO'] not in [
            '/rpc/BatchReqest_MakeCache_Login1',
            '/rpc/BatchReqest_MakeCache_Login2',
        ]:
            print(json.dumps(response.data, cls=CustomJSONEncoder, indent=2))   # For debugging
        response = json.dumps(response.data, cls=CustomJSONEncoder,
                              separators=(',', ':'))
        response = encrypt_response(response)

        start_response(status, headers)
        return [response]

    else:
        status = '503 Service Unavailable'
        headers = [('Content-Type', 'text/html')]
        start_response(status, headers)
        return [b'503 Service Unavailable']

