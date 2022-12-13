from argparse import ArgumentParser
from time import sleep
import subprocess
import endpoints

# parse arguments and store them accordingly
parser = ArgumentParser(
    prog="deployCDN", description="deploy necessary resources to set up a CDN"
)
parser.add_argument("-p", dest="port")
parser.add_argument("-o", dest="origin")
parser.add_argument("-n", dest="name")
parser.add_argument("-u", dest="username")
parser.add_argument("-i", dest="keyfile")

args = parser.parse_args()

if args.port is None:
    raise ValueError("No value for port supplied")
if args.origin is None:
    raise ValueError("No value for origin supplied")
if args.name is None:
    raise ValueError("No value for name supplied")
if args.username is None:
    raise ValueError("No value for username supplied")
if args.keyfile is None:
    raise ValueError("No value for keyfile supplied")

PORT = args.port
ORIGIN = args.origin
NAME = args.name
USERNAME = args.username
KEYFILE = args.keyfile


# start DNS script/server
subprocess.Popen(
    f"ssh -i {KEYFILE} {USERNAME}@{endpoints.DNS_SERVER} '~/dnsserver -p {PORT} -n {NAME} > /dev/null &'",
    shell=True,
)
print("DNS running and detached")


# start HTTP scritps/servers
for rep in endpoints.HTTP_REPLICAS:
    subprocess.Popen(
        f"ssh -i {KEYFILE} {USERNAME}@{rep} '~/httpserver -p {PORT} -o {ORIGIN} > /dev/null &'",
        shell=True,
    )
    print(f"{rep} running and detached")
