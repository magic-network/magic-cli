from os import remove
from jinja2 import Environment, FileSystemLoader
import getpass

from magic.definitions import RESOURCES_PATH, MAGIC_SSID_PREFIX
from magic.wireless.wireless_driver import WirelessDriver
from magic.util.cmd import cmd
from magic.util.prompt import get_prompt
from magic.util.log import log


class LinuxNmcli(WirelessDriver):
    _interface = None

    def __init__(self):
        self.wifi = WiFi()

    @staticmethod
    def get_mobileconfig_name(ssid, username):
        return ssid
        # return "%s-%s" % (ssid, username)

    def has_8021x_creds(self, ssid, address, signature):
        mobileconfig_name = self.get_mobileconfig_name(ssid, address)
        interface = self.interface()
        if len(interface) == 0:
            return None
        response = cmd("nmcli -t -f 802-1x.eap conn show " + ssid)
        has_config = False
        for line in response.stdout.splitlines():
            line_field, line_value = line.split(":")
            if line_field == "802-1x.eap" and line_value == "ttls":
                has_config = True
                break
        return has_config

    def install_8021x_creds(self, ssid, address, signature, timestamp):
        mobileconfig_name = self.get_mobileconfig_name(ssid, address)
        response = cmd('nmcli con add type wifi ifname %s con-name %s ssid %s ipv4.method auto 802-1x.eap ttls 802-1x.phase2-auth pap 802-1x.identity %s 802-1x.password %s-%s 802-11-wireless-security.key-mgmt wpa-eap' %
                       (self.interface(), mobileconfig_name, ssid, address, timestamp, signature))
        if not response.returncode == 0:
            log("An error occured: %s" % response.stdout, "red")
            return False
        return True

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
    def scan_networks(self, scan_interval):
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
        pass

    def get_wifistatus(self):
        response = cmd("nmcli radio wifi")
        if "enabled" in response.stdout:
            return "Yes"
        return "No"

    def get_ssid(self):
        response = cmd("nmcli -t -f active,ssid dev wifi")
        ssid = ""
        for line in response.stdout.splitlines():
            line_status, line_ssid = line.split(":")
            if line_status == "yes":
                ssid = line_ssid
        return ssid

    def scan(self, ssid=None):
        response = cmd("nmcli -t -f active,ssid dev wifi list")
        ssids = []
        for line in response.stdout.splitlines():
            line_status, line_ssid = line.split(":")
            if ssid == None or ssid == line_ssid:
                ssids.append(line_ssid)
        return ssids

    def associate(self, ssid):
        response = cmd("nmcli con up %s" % ssid)
        if not response.returncode == 0:
            log("An error occured: %s" % response.stdout, "red")
            return False
        return True

    def get_interface(self):
        response = cmd("nmcli -t -f device,type dev")
        interface = ""
        for line in response.stdout.splitlines():
            line_interface, line_type = line.split(":")
            if line_type == "wifi":
                interface = line_interface
        return interface

    def get_hardwareaddress(self):
        interface = self.get_interface()
        if len(interface) == 0:
            return None
        response = cmd("nmcli -t -f general.hwaddr dev show " + interface)
        hwaddr = ""
        for line in response.stdout.splitlines():
            line_field, line_hwaddr = line.split(":")
            if line_field == "GENERAL.HWADDR":
                hwaddr = line_hwaddr
        return hwaddr

    def get_aggregatenoise(self):
        # TODO
        return None

    def get_aggregaterssi(self):
        # TODO
        return None

    def get_bssid(self):
        response = cmd("nmcli -t -f active,bssid dev wifi")
        bssid = ""
        for line in response.stdout.splitlines():
            line_status, line_bssid = line.split(":")
            if line_status == "yes":
                bssid = line_bssid
        return bssid

    def get_channel(self):
        response = cmd("nmcli -t -f active,chan dev wifi")
        chan = ""
        for line in response.stdout.splitlines():
            line_status, line_chan = line.split(":")
            if line_status == "yes":
                chan = line_chan
        return chan

    def get_transmitrate(self):
        # TODO
        return None

    def get_mcsindex(self):
        # TODO
        return None
