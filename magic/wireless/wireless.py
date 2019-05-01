from magic.util.log import log
from magic.util.cmd import cmd
import platform


class Wireless:
    _driver_name = None
    _driver = None

    def __init__(self, interface=None):
        # Detect the platform's driver
        self._driver_name = self.detect_driver()
        log("Found driver: %s" % self._driver_name, 'blue')
        if self._driver_name == 'networksetup':
            from magic.wireless.driver.macos_networksetup import MacOSNetworksetup
            self._driver = MacOSNetworksetup()
        elif self._driver_name == 'nmcli':
            from magic.wireless.driver.linux_nmcli import LinuxNmcli
            self._driver = LinuxNmcli()
        elif self._driver_name == 'windows':
            from magic.wireless.driver.windows_wlanapi import WindowsNetworkSetup
            self._driver = WindowsNetworkSetup()

        # Raise an error if interface cannot be determined
        if self.interface() is None:
            raise Exception('Unable to auto-detect the network interface.')

    @staticmethod
    def detect_driver():

        # Windows
        # do this first because which doesn't exist for windows cmd
        if platform.system() == 'Windows':
            return 'windows'
        # MacOS
        response = cmd('which networksetup')
        if len(response.stdout) > 0 and 'not found' not in response.stdout:
            return 'networksetup'
        # Linux
        response = cmd('which nmcli')
        if len(response.stdout) > 0 and 'not found' not in response.stdout:
            return 'nmcli'
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
    def scan(self, scan_interval):
        networks = self._driver.scan_networks(scan_interval)
        log("Scan found %d magic networks available." % len(networks), 'white')
        return networks

    # Return the current wireless adapter
    def interface(self, interface=None):
        return self._driver.interface(interface)

    # Return the driver name
    def driver(self):
        return self._driver_name
