from multiprocessing import Process, freeze_support
from time import sleep

from mltd.servers import api_server, dns, proxy

_api_port = 8443
_proxy_port = 443
_dns_port = 53


if __name__ == '__main__':
    freeze_support()

    api_process = Process(target=api_server.start,
                          args=(_api_port,), daemon=True)
    api_process.start()
    proxy_process = Process(target=proxy.start,
                            args=(_proxy_port,), daemon=True)
    proxy_process.start()
    dns.start(_dns_port)

    api_process.join()
    proxy_process.join()

    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        pass

