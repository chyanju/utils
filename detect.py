import socket
import argparse
import ipaddress
import configparser

from pathlib import Path
from tabulate import tabulate

from paramiko import SSHClient, AutoAddPolicy
from paramiko import AuthenticationException

def run_command(cli, cmd):
    stdin, stdout, stderr = cli.exec_command(cmd)
    stdin.close()
    raw = "".join(stdout.readlines())
    return raw

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
args = ap.parse_args()

all_usernames = ["ubuntu", "zorin"]
all_ips = [str(ip) for ip in ipaddress.IPv4Network(args.network)]
avail_hosts = []
for ip_addr in all_ips:
    print(f"\r\b# scanning {ip_addr}", end="")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.1)
    result = sock.connect_ex((ip_addr,22))
    if result == 0:
        # print(f"{ip_addr} -> open")
        avail_hosts.append(ip_addr)
    else:
        # print(f"{ip_addr} -> closed")
        pass
    sock.close()
print("\r\b# done scanning                    ")

results = []
for ip_addr in avail_hosts:
    print(f"\r\b# talking with {ip_addr}", end="")
    client = SSHClient()
    client.set_missing_host_key_policy(AutoAddPolicy())

    # try different usernames
    for un in all_usernames:
        try:
            client.connect(ip_addr, username=un, key_filename=str(Path.home() / ".ssh" / "id-ed25519-ubuntu"))
            break
        except AuthenticationException:
            continue
    
    # get hostname and username
    hostname = run_command(client, "hostname").strip()
    username = run_command(client, "whoami").strip()

    # get release info
    release_raw = run_command(client, "cat /etc/*-release")
    release_raw = "[DEFAULT]\n" + release_raw
    cf = configparser.ConfigParser()
    cf.read_string(release_raw)
    system = cf["DEFAULT"]["PRETTY_NAME"].strip('"')

    results.append({
        "ip": ip_addr,
        "hostname": hostname,
        "username": username,
        "system": system,
    })
    client.close()
print("\r\b# done talking                    ")

headers = ["ip", "system", "hostname", "username"]
pcs = [
    (p["ip"], p["system"], p["hostname"], p["username"])
    for p in results
]
print(tabulate(pcs, headers=headers, showindex=True, tablefmt="github"))
