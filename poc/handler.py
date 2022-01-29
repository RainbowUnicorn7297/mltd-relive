from assets import asset

def application(environ, start_response):
##    print('\n'.join([str(('%s: %s' % (key, value)).encode('utf-8'))
##                     for key, value in environ.items()]))

    host = environ['HTTP_HOST']

    if host == 'd3k5923sb1sy5k.cloudfront.net' or \
       host == 'd1jbhqydw6nrn1.cloudfront.net':
        status = '200 OK'
        headers = [('Content-Type', 'application/octet-stream')]
    
        start_response(status, headers)

        tokens = environ['PATH_INFO'].split('/')
        return [asset('zh' if host == 'd3k5923sb1sy5k.cloudfront.net' else 'ko',
                     tokens[-2], tokens[-1])]
    elif host == 'theaterdays-zh.appspot.com' or \
         host == 'theaterdays-ko.appspot.com':
        status = '200 OK'
        headers = [('Content-Type', 'application/json'),
                   ('X-Encryption', 'on'),
                   ('X-Encryption-Compress', 'gzip'),
                   ('X-Encryption-Mode', '3')]

        start_response(status, headers)

        tokens = environ['PATH_INFO'].split('/')
        if tokens[-1] == 'GrecoService.AppBoot':
            return [b'1NzbIJMBO_44UDat84Ie6oj5Jzerxa3FmgLJTqKXhN-cFv85EFdXagBscxpZvtUGmu-0o5eOVi4XORUN-TvuiRPaB3oETdIO_giVfCmyfQs=']
        elif tokens[-1] == 'GameService.GetVersion':
            return [b'ECFgxyPGblwZo_xdafSu2O24jrHiJY9IJURP846gpKmbM2_wk4N5Kq9J3zra66aybkLKUmSEWHw8Dv0kaB-rzBALPwElXSWEJT01IpzUX0I4h63EAenFpl7ay8NTDTqP3EtCZS0dy-5DzeiYZ9SpXxgVtIH6W6rO6FP3mFL0kg6H-2syULm-tpEqzm3LGNyV6qWGQ8uSQM-mq0boc0vWEZSprkOTD46Zi-kEd_VDHUkr9wzA29U3RDw-ZlC_wPz1THdLLC-IehKwmuunvvaY-prlHTAe2JWstJNEWgKMLoZ9lgOPGVtybs45AGFNZlk0Xa_BnKR96ITcrWLy9j5qsdlrBwRFdkXlR4Lx4t-m5xonNnkE-jtDeggUqpSIq9xia3j2TtwAmF8_Ouxtj13cEDQJJ-upo27txdWQk_2rKyKD5bYCLB6SKL0MUSZzW0MD3NllssvoNG4wsghTIi-IAhMc0oZmkteTACJJ3y33zRCh6UC-CNeVm8OKVOt_M4-TDVORXhtNv_KTA2bd3yN2jmWGNimEfOpuNlyddUPC_fAgZx1uDsCpUSGA85f0TdeuwDB-JhA6zttbCzqC1wec4ovn9NUd9KUbDsVRaPwDgRo=']
    else:
        status = '503 Service Unavailable'
        headers = [('Content-Type', 'text/html')]
        
        start_response(status, headers)

        return [b'']
