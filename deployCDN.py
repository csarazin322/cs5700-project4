from argparse import ArgumentParser
from asyncio import sleep
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
subprocess.Popen(
    f"scp -i {KEYFILE} GeoLite2-City.mmdb {USERNAME}@{endpoints.DNS_SERVER}:~",
    shell=True,
)
subprocess.run(
    f"ssh -i {KEYFILE} {USERNAME}@{endpoints.DNS_SERVER} 'chmod 711 ~/dnsserver & pip install geoip2'",
    shell=True,
)


# deploy HTTP server code and chmod 711
preloading_procs: list[subprocess.Popen[bytes]] = []
for rep in endpoints.HTTP_REPLICAS:
    # file_to_copy = ["httpserver", "preLoadCache.py", "topPages.py"]
    subprocess.run(
        f"scp -i {KEYFILE} httpserver {USERNAME}@{rep}:~",
        shell=True,
    )
    p = subprocess.Popen(
        f"scp -i {KEYFILE} web_cache.db {USERNAME}@{rep}:~",
        shell=True,
    )
    subprocess.run(
        f"ssh -i {KEYFILE} {USERNAME}@{rep} 'chmod 711 ~/httpserver'",
        shell=True,
    )
    # p = subprocess.Popen(
    #     f"ssh -i {KEYFILE} {USERNAME}@{rep} 'chmod 711 ~/httpserver ~/preLoadCache && ~/preLoadCache && rm ~/preLoadCache'",
    #     shell=True,
    # )
    preloading_procs.append(p)

# wait for all processes to finish so user does not start servers before they are done pre-cacheing
p_count = 1
for proc in preloading_procs:
    print(f"Waiting for process {p_count} to finish")
    proc.wait()
    print(f"Process {p_count} finished")
    p_count += 1
