from argparse import ArgumentParser
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

print(PORT)
print(ORIGIN)
print(NAME)
print(USERNAME)
print(KEYFILE)

# deploy DNS code and chmod 711
b = subprocess.check_output("pwd")
print(b)
subprocess.run(
    f"scp -i {KEYFILE} dnsserver {USERNAME}@{endpoints.DNS_SERVER}:~",
    shell=True,
)
subprocess.run(
    f"scp -i {KEYFILE} GeoLite2-City.mmdb {USERNAME}@{endpoints.DNS_SERVER}:~",
    shell=True,
)
subprocess.run(
    f"ssh -i {KEYFILE} {USERNAME}@{endpoints.DNS_SERVER} 'chmod 711 ~/dnsserver & pip install geoip2'",
    shell=True,
)


# deploy HTTP server code and chmod 711
for rep in endpoints.HTTP_REPLICAS:
    # file_to_copy = ["httpserver", "preLoadCache.py", "topPages.py"]
    subprocess.run(f"scp -i {KEYFILE} preLoadCache.py {USERNAME}@{rep}:~", shell=True)
    subprocess.run(f"scp -i {KEYFILE} httpserver {USERNAME}@{rep}:~", shell=True)
    subprocess.run(f"scp -i {KEYFILE} topPages.py {USERNAME}@{rep}:~", shell=True)
    subprocess.run(
        f"ssh -i {KEYFILE} {USERNAME}@{rep} 'chmod 711 ~/httpserver & python3 ~/preLoadCache.py & rm ~/preLoadCache.py & rm ~/topPages.py & rm -rf ~/__pycache__'",
        shell=True,
    )
