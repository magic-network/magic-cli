from os import remove
from jinja2 import Environment, FileSystemLoader
import getpass
import objc

from magic.definitions import RESOURCES_PATH, MAGIC_SSID_PREFIX
from magic.wireless.wireless_driver import WirelessDriver
from magic.util.cmd import cmd
from magic.util.prompt import get_prompt
from magic.util.log import log

# noinspection PyUnresolvedReferences
objc.loadBundle('CoreWLAN',
                bundle_path='/System/Library/Frameworks/CoreWLAN.framework',
                module_globals=globals())


class MacOSNetworksetup(WirelessDriver):
    _interface = None

    def __init__(self):
        self.wifi = WiFi()

    @staticmethod
    def get_mobileconfig_name(ssid, username):
        return "%s-%s" % (ssid, username)

    def has_8021x_creds(self, ssid, address, signature):
        mobileconfig_name = self.get_mobileconfig_name(ssid, address)
        command = '''profiles -Lv | grep "name: %s" -4 | awk -F": " "/attribute: profileIdentifier/{print $NF}" ''' % \
                  mobileconfig_name
        response = cmd(command)

        if not response.stdout:
            return False
        else:
            return True

    def install_8021x_creds(self, ssid, address, signature, timestamp):
        template_env = Environment(loader=FileSystemLoader(RESOURCES_PATH))
        mobileconfig_name = self.get_mobileconfig_name(ssid, address)

        print("python radiusauth.py -s /tmp/magicsock %s %s-%s" %
              (address, timestamp, signature))

        rendered_mobileconfig = template_env.get_template('magic.appleconfig.template').render(
            address=address,
            signature=signature,
            ssid=ssid,
            name=mobileconfig_name,
            timestamp=timestamp
        )

        log("As a first time user, Magic will install a network profile to make connecting to the network easier.",
            "blue")

        try:
            passwd_prompt = get_prompt([{
                'type': 'password',
                'message': 'Enter your computer password',
                'name': 'password'
            }])

            passwd = passwd_prompt.get('password') + "\n"

        except Exception as error:
            raise Exception("An error occured: %s" % error)

        mobileconfig_filename = "%s.mobileconfig" % mobileconfig_name
        mobileconfig_file = open(
            "%s/%s" % (RESOURCES_PATH, mobileconfig_filename), "w")
        mobileconfig_file.write(rendered_mobileconfig)
        mobileconfig_file.close()

        response = cmd(
            "profiles install -path=%s/%s -user=%s" % (
                RESOURCES_PATH, mobileconfig_filename, getpass.getuser()),
            True,
            passwd.encode()
        )

        # Remove generated mobileconfig
        remove("%s/%s" % (RESOURCES_PATH, mobileconfig_filename))

        if not response.returncode == 0:
            log("An error occured: %s" % response.stdout, "red")
            return False

    # Connect to a network by SSID
    def connect(self, ssid):
        networks, error = self.wifi.interface.scanForNetworksWithName_error_(
            ssid, None)
        network = networks.anyObject()
        success, error = self.wifi.interface.associateToEnterpriseNetwork_identity_username_password_error_(
            network, None, None, None, None)
        return success

    # Return current SSID
    def current_ssid(self):
        return self.wifi.get_ssid()

    # Return a list of networks
    def scan_networks(self, scan_interval):
        ssids = []
        try:
            scan_results = self.wifi.interface.scanForNetworksWithName_includeHidden_error_(
                None, True, None)
        except AttributeError:
            # The includeHidden parameter is only available on OSX 10.13+
            scan_results = self.wifi.interface.scanForNetworksWithName_error_(
                None, None)

        for network in scan_results[0]:
            ssid = network.ssid()

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
        self.wifi = CWInterface.interfaceNames()
        for iname in self.wifi:
            self.interface = CWInterface.interfaceWithName_(iname)

    def get_wifistatus(self):
        if self.interface.powerOn() == 1:
            return "Yes"
        return "No"

    def get_ssid(self):
        return self.interface.ssid()

    def get_interface(self):
        return self.interface.interfaceName()

    def get_hardwareaddress(self):
        return self.interface.hardwareAddress()

    def get_aggregatenoise(self):
        return self.interface.aggregateNoise()

    def get_aggregaterssi(self):
        return self.interface.aggregateRSSI()

    def get_bssid(self):
        return self.interface.bssid()

    def get_channel(self):
        return self.interface.channel()

    def get_transmitrate(self):
        return self.interface.transmitRate()

    def get_mcsindex(self):
        return self.interface.mcsIndex()
