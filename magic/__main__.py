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
from magic.account.channel_manager import ChannelManager
from magic.util.log import log

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

    network_manager = NetworkManager()
    channel_manager = ChannelManager()
    account_manager = AccountManager(channel_manager)
    network_daemon = NetworkMonitor(10)

    account_manager.get_user()

    # Let developers choose the ssid of the magic network they'd like to connect to.
    if DEV:
        network_manager.get_custom_network_ssid()

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
