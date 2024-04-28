import web
import json
import socket
import argparse
import platform
import os
import web
import getpass
import distro
# from netifaces import interfaces, ifaddresses, AF_INET
import netifaces

ap = argparse.ArgumentParser()
ap.add_argument(
    "-p",
    "--port",
    default=7777,
    type=int,
    help="port of the info service, default: 7777",
)
args = ap.parse_args()

urls = (
    '/(.*)', 'info'
)
app = web.application(urls, globals())

class info:
    def GET(self, name):
        # ip_list = []
        # for interface in interfaces():
        #     for link in ifaddresses(interface)[AF_INET]:
        #         ip_list.append(link['addr'])
        ip_list = [netifaces.ifaddresses(iface)[netifaces.AF_INET][0]['addr'] for iface in netifaces.interfaces() if netifaces.AF_INET in netifaces.ifaddresses(iface)]
        info = {
            "hostname": socket.gethostname(),
            # "ip": socket.gethostbyname(socket.gethostname()),
            "ips": ip_list,
            "system": platform.system(),
            "distribution": distro.id(),
            "release": platform.release(),
            "user": getpass.getuser(),
        }
        web.header('Content-Type', 'application/json')
        return json.dumps(info)

if __name__ == "__main__":
    web.httpserver.runsimple(app.wsgifunc(), ("0.0.0.0", args.port))