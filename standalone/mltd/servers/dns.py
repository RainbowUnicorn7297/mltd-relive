from inspect import cleandoc
from socket import AF_INET, SOCK_DGRAM, socket
from time import sleep

from dnslib.intercept import InterceptResolver
from dnslib.server import DNSLogger, DNSServer

from mltd.servers.logging import logger

_port = 53


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
    zone_record = cleandoc(f"""
        theaterdays-zh.appspot.com. 60 IN A {lan_ip}
        theaterdays-ko.appspot.com. 60 IN A {lan_ip}
    """)

    resolver = InterceptResolver(address='8.8.8.8',
                                 port=53,
                                 ttl='60s',
                                 intercept=[zone_record],
                                 skip=[],
                                 nxdomain=[],
                                 forward=[],
                                 all_qtypes=False,
                                 timeout=5)
    dns_logger = DNSLogger(logf=logger.debug)
    udp_server = DNSServer(resolver, port=port, logger=dns_logger)
    logger.info(f'DNS is running on port {port}...')
    udp_server.start_thread()


if __name__ == '__main__':
    start(_port)
    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        pass

