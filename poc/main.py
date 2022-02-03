from multiprocessing import Process
from time import sleep
import api_server
import proxy
import dns

api_port = 8443
proxy_port = 443
dns_port = 53

if __name__ == "__main__":
    api_process = Process(target=api_server.start,
                          args=(api_port,), daemon=True)
    api_process.start()

    proxy_process = Process(target=proxy.start,
                            args=(proxy_port,), daemon=True)
    proxy_process.start()

    dns.start(dns_port)

    try:
        api_process.join()
        proxy_process.join()
    except KeyboardInterrupt:
        pass
