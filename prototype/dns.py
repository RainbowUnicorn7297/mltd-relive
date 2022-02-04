from dnslib.intercept import InterceptResolver
from dnslib.server import DNSServer
from socket import socket, AF_INET, SOCK_DGRAM
from time import sleep

port = 53

def get_ip():
    s = socket(AF_INET, SOCK_DGRAM)
    s.settimeout(0)
    try:
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

def start(port):
    lan_ip = get_ip()
    zone_record = f'''
theaterdays-zh.appspot.com. 60 IN A {lan_ip}
theaterdays-ko.appspot.com. 60 IN A {lan_ip}
'''

    resolver = InterceptResolver('8.8.8.8',     #upstream address
                                 53,            #upstream port
                                 '60s',         #ttl
                                 [zone_record], #incercept
                                 [],            #skip
                                 [],            #nxdomain
                                 [],            #forward
                                 False,         #all_qtypes
                                 5)             #timeout
    udp_server = DNSServer(resolver, port=port)
    print(f'DNS is running on port {port}...')
    udp_server.start_thread()

if __name__ == '__main__':
    start(port)
    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        pass
