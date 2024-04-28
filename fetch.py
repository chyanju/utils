import urllib.request
import json
import argparse
import ipaddress
from tabulate import tabulate

ap = argparse.ArgumentParser()
ap.add_argument(
    "-t", "--timeout", default=0.1, type=float, help="timeout, default: 0.1"
)
ap.add_argument(
    "-n",
    "--network",
    default="192.168.0.0/24",
    type=str,
    help="network to scan (in CIDR notation), default: 192.168.0.0/24",
)
ap.add_argument(
    "-p",
    "--port",
    default=7777,
    type=int,
    help="port of the info service, default: 7777",
)
args = ap.parse_args()

all_ips = [str(ip) for ip in ipaddress.IPv4Network(args.network)]
all_machines = []
for ip in all_ips:
    print(f"\r\bfetching {ip}", end="")
    try:
        contents = urllib.request.urlopen(
            f"http://{ip}:{args.port}/", timeout=args.timeout
        ).read()
        jc = json.loads(contents.decode("utf-8"))
        # filter out 127.0.0.1
        jc["ips"] = [p for p in jc["ips"] if p != "127.0.0.1"]
        all_machines.append(jc)
    except:
        continue
print(f"\r\b", end="")

headers = ["hostname", "system", "distribution", "release", "user", "ips"]
pcs = [
    (p["hostname"], p["system"], p["distribution"], p["release"], p["user"], p["ips"])
    for p in all_machines
]
print(tabulate(pcs, headers=headers, showindex=True, tablefmt="github"))
