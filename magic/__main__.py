#!/usr/bin/env python

# magic-cli - Command Line Interface (CLI) for connecting to the Magic Network
#
# Author: Magic Foundation <support@hologram.io>
#
# Copyright 2018 - Magic Foundation
#
#
# LICENSE: Distributed under the terms of the MIT License
import signal
import click
from magic.daemon.network_monitor import NetworkMonitor
from magic.account.account_manager import AccountManager
from magic.network.network_manager import NetworkManager
from magic.wireless.wireless import Wireless
from magic.util.prompt import get_prompt, tryconvert
from magic.util.log import log
from yaspin import yaspin

import sys

DEV = True

# Filter ANSI escape sequences for colored terminal text under Windows
try:
    import colorama
    colorama.init()
except ImportError:
    colorama = None


class context:
    y = False


def sighandler(signum, frame):
    if signum == signal.SIGTERM:
        log("Got SIGTERM. Shutting down.", "red")
        context.y = True
    elif signum == signal.SIGINT:
        log("Got SIGINT. Shutting down.", "red")
        context.y = True
    else:
        log("Signal %d not handled" % signum, "red")


@click.command()
def main():
    """
    CLI for connecting to the Magic Network
    """
    print("\t")
    log("M a g i c", color="blue", figlet=True)
    print("\t")
    log("Welcome to Magic", "green")
    print("\t")

    wireless = Wireless()
    network_manager = NetworkManager(wireless)
    account_manager = AccountManager(wireless)
    network_daemon = NetworkMonitor(10)

    # Setup initial user account data
    account_manager.get_critical_info()

    ssids = None

    if DEV:
        # Scan for local networks
        answers = get_prompt([ {
                'type': 'input',
                'name': 'wait_time',
                'message': 'How many seconds to scan for magic networks?',
                'default': '10'
        }])

        with yaspin():
            ssids = wireless.scan(int(answers['wait_time']))
        
        network_manager.get_custom_network_ssid(ssids)

        if not ssids:
            log("Could not find any magic ssids!", "red")
            sys.exit(1)
    
    # Make sure any profiles or wpa_supplicants are installed.
    account_manager.setup_8021x_creds(network_manager.ssid)

    # Kick off connection process
    network_manager.connect()

    signal.signal(signal.SIGTERM, sighandler)
    signal.signal(signal.SIGINT, sighandler)

    # TODO: WIP connection monitor
    # network_daemon.start()
    # while not context.y: time.sleep(1)


if __name__ == '__main__':
    main()
