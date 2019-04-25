from os import remove
import pywifi
from pywifi import const
import getpass

from magic.definitions import RESOURCES_PATH, MAGIC_SSID_PREFIX
from magic.wireless.wireless_driver import WirelessDriver
from magic.util.cmd import cmd
from magic.util.prompt import get_prompt
from magic.util.log import log


class WindowsNetworkSetup(WirelessDriver):
    def __init__(self):
        self.wifi = WiFi()

    @staticmethod
    def get_mobileconfig_name(ssid, username):
        return "%s-%s" % (ssid, username)

    # def has_8021x_creds(self, ssid, address, signature):
    #     mobileconfig_name = self.get_mobileconfig_name(ssid, address)
    #     interface = self._interface()
    #     if len(interface) == 0: return None
    #     response = cmd("nmcli -t -f 802-1x.eap conn show " + ssid)
    #     has_config = False
    #     for line in response.stdout.splitlines():
    #         line_field,line_value = line.split(":")
    #         if line_field == "802-1x.eap" and line_value == "ttls":
    #             has_config = True
    #             break
    #     return has_config

    # def install_8021x_creds(self, ssid, address, signature, timestamp):
    #     mobileconfig_name = self.get_mobileconfig_name(ssid, address)
    #     response = cmd('nmcli con add type wifi ifname %s con-name %s ssid %s ipv4.method auto 802-1x.eap ttls 802-1x.phase2-auth pap 802-1x.identity %s 802-1x.password %s-%s 802-11-wireless-security.key-mgmt wpa-eap' % (self._interface(), mobileconfig_name, ssid, address, timestamp, signature))
    #     if not response.returncode == 0:
    #         log("An error occured: %s" % response.stdout, "red")
    #         return False
    #     return True
        
    # Connect to a network by SSID
    def connect(self, ssid):
        success = False
        networks = self.wifi.scan(ssid)
        if len(networks) > 0:
            network = networks[0]
            success = self.wifi.associate(network)
        return success

    # Return current SSID
    def current_ssid(self):
        return self.wifi.get_ssid()

    # Return a list of networks
    def scan_networks(self):
        ssids = []
        scan_results = self.wifi.scan()
        for ssid in scan_results:
            if ssid is None:
                continue
            if ssid.startswith(MAGIC_SSID_PREFIX):
                ssids.append(ssid)
        return ssids

    # Return the current wireless adapter
    def interface(self, interface=None):
        return self.wifi.get_interface()


class WiFi(object):
    def __init__(self):
        self._wifi = pywifi.PyWiFi()
        self._interface = None
        #if we are connected already set that as the current interface
        for iface in self._wifi.interfaces():
            if iface.status() in [const.IFACE_CONNECTED]:
                self._interface = iface

    def get_wifistatus(self):
        if self._interface and self._interface.status() in [const.IFACE_CONNECTED]:
            return "Yes"
        return "No"

    def get_ssid(self):
        ssid = ""
        for profile in self._interface.network_profiles:
            if self.get_wifistatus() == "yes":
                ssid = profile.ssid
        return ssid
    
    def scan(self,ssid=None):
        self._wifi.scan()
        ssids = []
        for result in self._wifi.scan_results:
            if ssid == None or ssid == result.ssid:
                ssids.append(result.ssid)
        return ssids
    
    def associate(self,ssid):
        profile = pywifi.Profile()
        profile.ssid = ssid
        profile.auth = const.AUTH_ALG_OPEN
        profile.akm.append(const.AKM_TYPE_WPA2PSK)
        profile.cipher = const.CIPHER_TYPE_CCMP
        profile.key = '12345678' #maybe a random uuid or something

        tmp_profile = self._interface.add_network_profile(profile)

        return self._interface.connect(tmp_profile)


    def get_interface(self):
        return self._interface

    def get_hardwareaddress(self):
        # TODO
        return None

    def get_aggregatenoise(self):
        # TODO
        return None

    def get_aggregaterssi(self):
        # TODO
        return None

    def get_bssid(self):
        bssid = ""
        for profile in self._interface.network_profiles:
            if self.get_wifistatus() == "yes":
                bssid = profile.bssid
        return bssid
    
    def get_channel(self):
        # TODO
        return None

    def get_transmitrate(self):
        # TODO
        return None

    def get_mcsindex(self):
        # TODO
        return None
