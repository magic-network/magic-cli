from magic.wireless.driver.macos_networksetup import MacOSNetworksetup
from magic.util.log import log
from magic.util.cmd import cmd


class Wireless:
    _driver_name = None
    _driver = None

    def __init__(self, interface=None):
        # Detect the platform's driver
        self._driver_name = self.detect_driver()
        if self._driver_name == 'networksetup':
            self._driver = MacOSNetworksetup()
        else:
            # TODO: Windows and Linux support
            log("Your OS is not supported yet.", "red")

        # Raise an error if interface cannot be determined
        if self.interface() is None:
            raise Exception('Unable to auto-detect the network interface.')

    @staticmethod
    def detect_driver():
        # MacOS
        response = cmd('which networksetup')
        if len(response.stdout) > 0 and 'not found' not in response.stdout:
            return 'networksetup'

        raise Exception('Unable to find compatible wireless driver.')

    # Check for existence of 8021x creds instalsled already
    def has_8021x_creds(self, ssid, address, signature):
        return self._driver.has_8021x_creds(ssid, address, signature)

    # Install proper creds for 802.1x connection
    def install_8021x_creds(self, ssid, address, signature, timestamp):
        return self._driver.install_8021x_creds(ssid, address, signature, timestamp)

    # Connect to a network by SSID
    def connect(self, ssid):
        return self._driver.connect(ssid)

    # Return SSID of the current network
    def current(self):
        return self._driver.current_ssid()

    # Return a list of networks
    def scan(self):
        return self._driver.scan_networks()

    # Return the current wireless adapter
    def interface(self, interface=None):
        return self._driver.interface(interface)

    # Return the driver name
    def driver(self):
        return self._driver_name
