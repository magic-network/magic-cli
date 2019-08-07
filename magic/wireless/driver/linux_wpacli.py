import os
import time
from jinja2 import Environment, FileSystemLoader
import getpass

from magic.definitions import RESOURCES_PATH, MAGIC_SSID_PREFIX
from magic.wireless.wireless_driver import WirelessDriver
from magic.util.cmd import cmd
from magic.util.prompt import get_prompt
from magic.util.log import log


class LinuxWPAcli(WirelessDriver):
    _interface = None

    def __init__(self):
        self.wifi = WiFi()

    @staticmethod
    def get_mobileconfig_name(ssid, username):
        return ssid

    def has_8021x_creds(self, ssid, address, signature):
        response = cmd("wpa_cli -i wlan0 list_networks")
        ssid = ""
        for line in response.stdout.splitlines()[1:]:
            net_id, n_ssid, bssid, flags = line.split("\t")
            if n_ssid == ssid:
                return True
        return False

    def install_8021x_creds(self, ssid, address, signature, timestamp):
        try:
            network_id = cmd('wpa_cli -i wlan0 add_network').stdout.strip(' \n\t\r')
            cert_path = os.path.dirname(os.path.realpath(__file__)) + "/../../resources/certs/server.pem"
            self.validate_response(cmd('wpa_cli -i wlan0 set_network {0} ssid \'"{1}"\''.format(network_id, ssid)))
            self.validate_response(cmd('wpa_cli -i wlan0 set_network {0} key_mgmt "WPA-EAP"'.format(network_id)))
            self.validate_response(cmd('wpa_cli -i wlan0 set_network {0} priority 1'.format(network_id)))
            self.validate_response(cmd('wpa_cli -i wlan0 set_network {0} group "CCMP"'.format(network_id)))
            self.validate_response(cmd('wpa_cli -i wlan0 set_network {0} eap "TTLS"'.format(network_id)))
            self.validate_response(cmd('wpa_cli -i wlan0 set_network {0} ca_cert "{1}"'.format(network_id, cert_path)))
            self.validate_response(cmd('wpa_cli -i wlan0 set_network {0} phase2 \'"auth=PAP"\''.format(network_id)))
            self.validate_response(cmd('wpa_cli -i wlan0 identity {0} "{1}"'.format(network_id, address)))
            self.validate_response(cmd('wpa_cli -i wlan0 password {0} "{1}"'.format(network_id, "{0}-{1}".format(timestamp, signature))))
            self.validate_response(cmd('wpa_cli -i wlan0 enable_network {0}'.format(network_id)))
            self.validate_response(cmd('wpa_cli -i wlan0 save_config'))
        except Exception:
            return False
        return True

    def validate_response(self, response):
        if "OK" not in response.stdout:
            raise Exception('wpa_cli command failed')

    # Connect to a network by SSID
    def connect(self, ssid):
        success = False
        networks = self.wifi.scan(ssid)
        if networks:
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


class WiFi():
    def __init__(self):
        pass

    def get_wifistatus(self):
        response = cmd("wpa_cli -i wlan0 status")
        for line in response.stdout.splitlines():
            line_key, line_val = line.split("=")
            if line_key == "wpa_state":
                return line_val is not "INACTIVE"
        return False

    def get_ssid(self):
        response = cmd("wpa_cli -i wlan0 status")
        ssid = ""
        for line in response.stdout.splitlines():
            line_key, line_val = line.split("=")
            if line_key == "ssid":
                return line_val
        return ssid

    def scan(self, ssid=None):
        cmd("wpa_cli -i wlan0 scan")
        time.sleep(3)
        response = cmd("wpa_cli -i wlan0 scan_results")
        ssids = []
        for line in response.stdout.splitlines()[1:]:
            bssid, freq, sig_str, flags, ssid = line.split("\t")
            if ssid is not None:
                ssids.append(ssid)
        return ssids

    def associate(self, ssid):
        response = cmd("wpa_cli -i wlan0 reconfigure")
        if response.returncode != 0:
            log("An error occured: %s" % response.stdout, "red")
            return False
        return True

    def get_interface(self):
        return "wlan0"

    def get_hardwareaddress(self):
        response = cmd("wpa_cli -i wlan0 status")
        hw_address = ""
        for line in response.stdout.splitlines():
            line_key, line_val = line.split("=")
            if line_key == "address":
                return line_val
        return hw_address

    def get_aggregatenoise(self):
        # TODO
        return None

    def get_aggregaterssi(self):
        # TODO
        return None

    def get_bssid(self):
        response = cmd("wpa_cli -i wlan0 status")
        bssid = ""
        for line in response.stdout.splitlines():
            line_key, line_val = line.split("=")
            if line_key == "bssid":
                return line_val
        return bssid

    def get_channel(self):
        return None

    def get_transmitrate(self):
        # TODO
        return None

    def get_mcsindex(self):
        # TODO
        return None
