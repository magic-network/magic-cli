import sys

from yaspin import yaspin

from magic.util.log import log
from magic.wireless.wireless import Wireless
from magic.util.prompt import get_prompt


class NetworkManager:
    def __init__(self, wireless=Wireless()):
        self.wireless = wireless
        self.current_network = None
        self.ssid = "magic"

    def get_custom_network_ssid(self, ssids):

        if not ssids:
            log("Could not find any magic ssids!", "red")
            sys.exit(1)

        answers = get_prompt([
            {
                'type': 'list',
                'name': 'ssid',
                'message': '(DEV) Select a magic ssid format:',
                'choices': ssids,
                'filter': lambda val: val.lower()
            }
        ])

        self.ssid = answers.get('ssid')

    def connect(self):
        # TODO: Find networks with the best signal, and connect to that one only.
        log("Magically connecting to the best network...", "yellow")

        with yaspin():
            success = self.wireless.connect(self.ssid)

        # TODO: Ping some endpoint until connectivity is guaranteed?
        if success:
            log("You're connected! Enjoy your magic internet.")
        else:
            log("Was not able to connect to the network :(", 'red')
