from multiprocessing import Process
from time import sleep

from mltd.servers import api_server, dns, proxy
from mltd.servers.logging import handler


if __name__ == '__main__':
    handler.doRollover()

    proxy_process = Process(target=proxy.start, daemon=True)
    proxy_process.start()
    api_process = Process(target=api_server.start, daemon=True)
    api_process.start()
    dns_process = Process(target=dns.start, daemon=True)
    dns_process.start()

    dns_process.join()
    api_process.join()
    proxy_process.join()

    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        pass

