from abc import ABCMeta, abstractmethod


class WirelessDriver:
    __metaclass__ = ABCMeta

    @abstractmethod
    def has_8021x_creds(self, ssid, address, signature):
        pass

    @abstractmethod
    def install_8021x_creds(self, ssid, address, signature, timestamp):
        pass

    @abstractmethod
    def connect(self, ssid):
        pass

    @abstractmethod
    def current_ssid(self):
        pass

    @abstractmethod
    def scan_networks(self):
        pass

    @abstractmethod
    def interface(self, interface=None):
        pass
