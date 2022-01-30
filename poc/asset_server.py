from wsgiref.simple_server import make_server
##from ssl import SSLContext, PROTOCOL_TLS_SERVER
from assets import asset

def application(environ, start_response):
    host = environ['HTTP_HOST']
    
    status = '200 OK'
    headers = [('Content-Type', 'application/octet-stream'),
##               ('Connection', 'close'),
               ('X-GUploader-UploadID', 'ADPycdvNpwvJkAOl68SLxwxhaAY3P2OeyTIrU3ZJsa6O5vz3I8-EnEa3NSRc0P6N3DSSkcvz-i6_c3wkbHme5ktSXQQPWQG4mg'),
               ('Last-Modified', 'Tue, 21 Sep 2021 01:18:30 GMT'),
               ('x-goog-generation', '1632187110670085'),
               ('x-goog-metageneration', '1'),
               ('x-goog-stored-content-encoding', 'identity'),
               ('x-goog-stored-content-length', '4268471'),
               ('x-goog-meta-goog-reserved-file-mtime', '1631271323'),
               ('x-goog-hash', 'crc32c=sOdsow=='),
               ('x-goog-hash', 'md5=4+eqb+lrq9yAbP+2IcQ8gw=='),
               ('x-goog-storage-class', 'REGIONAL'),
               ('Accept-Ranges', 'bytes'),
               ('Server', 'UploadServer'),
               ('Cache-Control', 'no-cache'),
               ('Expires', 'Thu, 19 Jan 2023 17:34:33 GMT'),
               ('ETag', '"e3e7aa6fe96babdc806cffb621c43c83"'),
               ('X-Cache', 'RefreshHit from cloudfront'),
               ('Via', '1.1 214d8a3cdb14de6b0331d1f72902cc66.cloudfront.net (CloudFront)'),
               ('X-Amz-Cf-Pop', 'HKG60-C1'),
               ('X-Amz-Cf-Id', '4EBHSJHsdAyhIhGHgXDtFpH-KdcwJ52oT_p9qbAA5LkM4C65w2rvUQ==')]

    start_response(status, headers)

    tokens = environ['PATH_INFO'].split('/')
    return [asset('zh' if host == 'd3k5923sb1sy5k.cloudfront.net' else 'ko',
                 tokens[-2], tokens[-1])]

with make_server('', 80, application) as httpd:
##    certfile = '../key/asset.crt'
##    keyfile = '../key/asset.key'
##    context = SSLContext(PROTOCOL_TLS_SERVER)
##    context.load_cert_chain(certfile, keyfile)
####    httpd.socket = wrap_socket(
####        httpd.socket, certfile=certfile, keyfile=keyfile, server_side=True)
##    httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
##    httpd.socket.accept()
    
    print('Serving HTTP on port 80...')
    httpd.serve_forever()
