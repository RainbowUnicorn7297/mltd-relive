from inspect import cleandoc
from time import sleep

import netifaces
from dnslib.intercept import InterceptResolver
from dnslib.server import DNSLogger, DNSServer

from mltd.servers.logging import logger

dns_port = 53


def get_lan_ips():
    try:
        iface = netifaces.gateways()['default'][netifaces.AF_INET][1]
        ipv4 = netifaces.ifaddresses(iface)[netifaces.AF_INET][0]['addr']
    except Exception:
        ipv4 = None
    try:
        iface = netifaces.gateways()['default'][netifaces.AF_INET6][1]
        ipv6 = netifaces.ifaddresses(iface)[netifaces.AF_INET6][0]['addr']
    except Exception:
        ipv6 = None
    return ipv4, ipv6


def start(port=dns_port):
    lan_ipv4, lan_ipv6 = get_lan_ips()
    zone_record = ''
    if lan_ipv4:
        zone_record = cleandoc(f"""
            theaterdays-zh.appspot.com. 60 IN A {lan_ipv4}
            theaterdays-ko.appspot.com. 60 IN A {lan_ipv4}
        """)
        zone_record += '\n'
    if lan_ipv6:
        zone_record = cleandoc(f"""
            theaterdays-zh.appspot.com. 60 IN A {lan_ipv6}
            theaterdays-ko.appspot.com. 60 IN A {lan_ipv6}
        """)
        zone_record += '\n'

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
    logger.info(f'IPv4: {lan_ipv4}')
    logger.info(f'IPv6: {lan_ipv6}')
    udp_server.start()


if __name__ == '__main__':
    start()
    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        pass

