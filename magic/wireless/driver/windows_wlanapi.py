import re
from jinja2 import Environment, FileSystemLoader
from ctypes.wintypes import *
from ctypes import *
import time
from os import remove
import platform
import getpass

from magic.definitions import RESOURCES_PATH, MAGIC_SSID_PREFIX
from magic.wireless.wireless_driver import WirelessDriver
from magic.util.cmd import cmd
from magic.util.prompt import get_prompt
from magic.util.log import log

if platform.system() is 'Windows':
    from comtypes import GUID

    if platform.release().lower() not in ['8', '10']:
        log("Magic CLI likely won't work on Windows versions earlier than 8", "red")


    class WindowsNetworkSetup(WirelessDriver):
        def __init__(self):
            self.wifi = WiFi()

        @staticmethod
        def get_mobileconfig_name(ssid, username):
            return "%s-%s" % (ssid, username)

        def has_8021x_creds(self, ssid, address, signature):
            mobileconfig_name = self.get_mobileconfig_name(ssid, address)
            profile_names = self.wifi.network_profile_name_list()
            for name in profile_names:
                if name == mobileconfig_name:
                    return True
            return False

        def install_8021x_creds(self, ssid, address, signature, timestamp):
            result = self.wifi.add_network_profile(self.get_mobileconfig_name(
                ssid, address), ssid, address, signature, timestamp)
            log("Installing network profile resulted in: %s" % result, 'yellow')

        # Connect to a network by SSID
        def connect(self, ssid):
            success = False
            networks = self.wifi.scan(5, ssid)
            if len(networks) > 0:
                network = networks[0]
                log("Connecting to network: %s" % network, 'white')
                success = self.wifi.connect(network)
            return success

        # Return current SSID
        def current_ssid(self):
            return self.wifi.get_ssid()

        # Return a list of networks
        def scan_networks(self, scan_interval):
            ssids = []
            scan_results = self.wifi.scan(scan_interval)
            for ssid in scan_results:
                if ssid is None:
                    continue
                if ssid.startswith(MAGIC_SSID_PREFIX):
                    ssids.append(ssid)
            return ssids

        # Return the current wireless adapter
        def interface(self, interface=None):
            return self.wifi.get_interface(interface)


    """
    Some types does not exist in python2 ctypes.wintypes so we fake them
    using how its defined in python3 ctypes.wintypes.
    """
    if "PDWORD" not in dir():
        PDWORD = POINTER(DWORD)

    if "PWCHAR" not in dir():
        PWCHAR = POINTER(WCHAR)

    ERROR_SUCCESS = 0
    WLAN_MAX_PHY_TYPE_NUMBER = 8
    DOT11_MAC_ADDRESS = c_ubyte * 6
    WLAN_CONNECTION_MODE = c_uint
    DOT11_BSS_TYPE = c_uint

    native_wifi = windll.wlanapi

    WLAN_INTERFACE_STATE = {0: "not_ready",
                            1: "connected",
                            2: "ad_hoc_network_formed",
                            3: "disconnecting",
                            4: "disconnected",
                            5: "associating",
                            6: "discovering",
                            7: "authenticating"}

    WLAN_INTERFACE_STATE_VK = {v: k for k, v in
                            WLAN_INTERFACE_STATE.items()}

    AUTH_ALGORITHM = {1: "80211_OPEN",
                    2: "80211_SHARED_KEY",
                    3: "WPA",
                    4: "WPA_PSK",
                    5: "WPA_NONE",
                    6: "RSNA",
                    7: "RSNA_PSK",
                    0x80000000: "IHV_START",
                    0xffffffff: "IHV_END"}

    CIPHER_ALGORITHM = {0x00: "NONE",
                        0x01: "WEP40",
                        0x02: "TKIP",
                        0x04: "CCMP",
                        0x05: "WEP104",
                        0x100: "WPA_USE_GROUP",
                        0x100: "RSN_USE_GROUP",
                        0x101: "WEP",
                        0x80000000: "IHV_START",
                        0xffffffff: "IHV_END"}

    WLAN_INTERFACE_OPCODES = {
        0x000000000: "autoconf_start",
        1: "autoconf_enabled",
        2: "background_scan_enabled",
        3: "media_streaming_mode",
        4: "radio_state",
        5: "bss_type",
        6: "interface_state",
        7: "current_connection",
        8: "channel_number",
        9: "supported_infrastructure_auth_cipher_pairs",
        10: "supported_adhoc_auth_cipher_pairs",
        11: "supported_country_or_region_string_list",
        12: "current_operation_mode",
        13: "supported_safe_mode",
        14: "certified_safe_mode",
        15: "hosted_network_capable",
        16: "management_frame_protection_capable",
        0x0fffffff: "autoconf_end",
        0x10000100: "msm_start",
        17: "statistics",
        18: "rssi",
        0x1fffffff: "msm_end",
        0x20010000: "security_start",
        0x2fffffff: "security_end",
        0x30000000: "ihv_start",
        0x3fffffff: "ihv_end"
    }

    WLAN_INTERFACE_OPCODES_VK = {v: k for k, v in
                                WLAN_INTERFACE_OPCODES.items()}


    class WLAN_INTERFACE_INFO(Structure):

        _fields_ = [
            ("InterfaceGuid", GUID),
            ("strInterfaceDescription", c_wchar * 256),
            ("isState", c_uint)
        ]


    class WLAN_INTERFACE_INFO_LIST(Structure):

        _fields_ = [
            ("dwNumberOfItems", DWORD),
            ("dwIndex", DWORD),
            ("InterfaceInfo", WLAN_INTERFACE_INFO * 1)
        ]


    DOT11_SSID_MAX_LENGTH = 32


    class DOT11_SSID(Structure):

        _fields_ = [("uSSIDLength", c_ulong),
                    ("ucSSID", c_char * DOT11_SSID_MAX_LENGTH)]


    class WLAN_RATE_SET(Structure):

        _fields_ = [
            ("uRateSetLength", c_ulong),
            ("usRateSet", c_ushort * 126)
        ]


    class WLAN_RAW_DATA(Structure):

        _fields_ = [
            ("dwDataSize", DWORD),
            ("DataBlob", c_byte * 1)
        ]


    class WLAN_AVAILABLE_NETWORK(Structure):

        _fields_ = [
            ("strProfileName", c_wchar * 256),
            ("dot11Ssid", DOT11_SSID),
            ("dot11BssType", c_uint),
            ("uNumberOfBssids", c_ulong),
            ("bNetworkConnectable", c_bool),
            ("wlanNotConnectableReason", c_uint),
            ("uNumberOfPhyTypes", c_ulong * WLAN_MAX_PHY_TYPE_NUMBER),
            ("dot11PhyTypes", c_uint),
            ("bMorePhyTypes", c_bool),
            ("wlanSignalQuality", c_ulong),
            ("bSecurityEnabled", c_bool),
            ("dot11DefaultAuthAlgorithm", c_uint),
            ("dot11DefaultCipherAlgorithm", c_uint),
            ("dwFlags", DWORD),
            ("dwReserved", DWORD)
        ]


    class WLAN_AVAILABLE_NETWORK_LIST(Structure):

        _fields_ = [
            ("dwNumberOfItems", DWORD),
            ("dwIndex", DWORD),
            ("Network", WLAN_AVAILABLE_NETWORK * 1)
        ]


    class WLAN_BSS_ENTRY(Structure):

        _fields_ = [
            ("dot11Ssid", DOT11_SSID),
            ("uPhyId", c_ulong),
            ("dot11Bssid", DOT11_MAC_ADDRESS),
            ("dot11BssType", c_uint),
            ("dot11BssPhyType", c_uint),
            ("lRssi", c_long),
            ("uLinkQuality", c_ulong),
            ("bInRegDomain", c_bool),
            ("usBeaconPeriod", c_ushort),
            ("ullTimestamp", c_ulonglong),
            ("ullHostTimestamp", c_ulonglong),
            ("usCapabilityInformation", c_ushort),
            ("ulChCenterFrequency", c_ulong),
            ("wlanRateSet", WLAN_RATE_SET),
            ("ulIeOffset", c_ulong),
            ("ulIeSize", c_ulong)
        ]


    class WLAN_BSS_LIST(Structure):

        _fields_ = [
            ("dwTotalSize", DWORD),
            ("dwNumberOfItems", DWORD),
            ("wlanBssEntries", WLAN_BSS_ENTRY * 1)
        ]


    class NDIS_OBJECT_HEADER(Structure):

        _fields_ = [
            ("Type", c_ubyte),
            ("Revision", c_ubyte),
            ("Size", c_ushort)
        ]


    class DOT11_BSSID_LIST(Structure):

        _fields_ = [
            ("Header", NDIS_OBJECT_HEADER),
            ("uNumOfEntries", c_ulong),
            ("uTotalNumOfEntries", c_ulong),
            ("BSSIDs", DOT11_MAC_ADDRESS * 1)
        ]


    class WLAN_CONNECTION_PARAMETERS(Structure):
        _fields_ = [("wlanConnectionMode", WLAN_CONNECTION_MODE),
                    ("strProfile", LPCWSTR),
                    ("pDot11_ssid", POINTER(DOT11_SSID)),
                    ("pDesiredBssidList", POINTER(DOT11_BSSID_LIST)),
                    ("dot11BssType", DOT11_BSS_TYPE),
                    ("dwFlags", DWORD)]


    class WLAN_PHY_RADIO_STATE(Structure):
        _fields_ = [("dwPhyIndex", DWORD),
                    ("dot11SoftwareRadioState", c_uint),
                    ("dot11HardwareRadioState", c_uint)]


    class WLAN_RADIO_STATE(Structure):
        _fields_ = [("dwNumberOfPhys", DWORD),
                    ("PhyRadioState", WLAN_PHY_RADIO_STATE * 64)]


    class WLAN_PROFILE_INFO(Structure):

        _fields_ = [
            ("strProfileName", c_wchar * 256),
            ("dwFlags", DWORD)
        ]


    class WLAN_PROFILE_INFO_LIST(Structure):

        _fields_ = [
            ("dwNumberOfItems", DWORD),
            ("dwIndex", DWORD),
            ("ProfileInfo", WLAN_PROFILE_INFO * 1)
        ]


    class WLAN_ASSOCIATION_ATTRIBUTES(Structure):
        _fields_ = [("dot11Ssid", DOT11_SSID),
                    ("dot11BssType", c_uint),
                    ("dot11Bssid", DOT11_MAC_ADDRESS),
                    ("dot11PhyType", c_uint),
                    ("uDot11PhyIndex", c_ulong),
                    ("wlanSignalQuality", c_ulong),
                    ("ulRxRate", c_ulong),
                    ("ulTxRate", c_ulong)]


    class WLAN_SECURITY_ATTRIBUTES(Structure):
        _fields_ = [("bSecurityEnabled", BOOL),
                    ("bOneXEnabled", BOOL),
                    ("dot11AuthAlgorithm", c_uint),
                    ("dot11CipherAlgorithm", c_uint)]


    class WLAN_CONNECTION_ATTRIBUTES(Structure):
        _fields_ = [("isState", c_uint),
                    ("wlanConnectionMode", c_uint),
                    ("strProfileName", c_wchar * 256),
                    ("wlanAssociationAttributes", WLAN_ASSOCIATION_ATTRIBUTES),
                    ("wlanSecurityAttributes", WLAN_SECURITY_ATTRIBUTES)]


    WLAN_INTF_OPCODE_TYPE_DICT = {
        "wlan_intf_opcode_autoconf_enabled": c_bool,
        "wlan_intf_opcode_background_scan_enabled": c_bool,
        "wlan_intf_opcode_radio_state": WLAN_RADIO_STATE,
        "wlan_intf_opcode_bss_type": c_uint,
        "wlan_intf_opcode_interface_state": c_uint,
        "wlan_intf_opcode_current_connection": WLAN_CONNECTION_ATTRIBUTES,
        "wlan_intf_opcode_channel_number": c_ulong,
        # "wlan_intf_opcode_supported_infrastructure_auth_cipher_pairs": \
        # WLAN_AUTH_CIPHER_PAIR_LIST,
        # "wlan_intf_opcode_supported_adhoc_auth_cipher_pairs": \
        # WLAN_AUTH_CIPHER_PAIR_LIST,
        # "wlan_intf_opcode_supported_country_or_region_string_list": \
        # WLAN_COUNTRY_OR_REGION_STRING_LIST,
        "wlan_intf_opcode_media_streaming_mode": c_bool,
        # "wlan_intf_opcode_statistics": WLAN_STATISTICS,
        "wlan_intf_opcode_rssi": c_long,
        "wlan_intf_opcode_current_operation_mode": c_ulong,
        "wlan_intf_opcode_supported_safe_mode": c_bool,
        "wlan_intf_opcode_certified_safe_mode": c_bool
    }


    class WiFi(object):
        _interfaces = pointer(WLAN_INTERFACE_INFO_LIST())
        _interface = POINTER(WLAN_INTERFACE_INFO)
        _handle = None

        def __init__(self):
            # Opens a handle and grabs all the interfaces
            self.interfaces()

            if self._interfaces.contents.dwNumberOfItems > 0:
                interfaces = cast(self._interfaces.contents.InterfaceInfo,
                                POINTER(WLAN_INTERFACE_INFO))
                # set the default one if none are connected
                self._interface = interfaces[0]
                for i in range(0, self._interfaces.contents.dwNumberOfItems):
                    if interfaces[i].isState in [
                            WLAN_INTERFACE_STATE_VK['connected'],
                            WLAN_INTERFACE_STATE_VK['ad_hoc_network_formed']]:
                        self._interface = interfaces[i]

        # make sure we close the handle when the object is destroyed
        def __del__(self):
            if self._handle is not None:
                self._wlan_close_handle(self._handle)

        def get_ssid(self):
            """Get the SSID of the currently connected network"""
            data = self._wlan_query_interface(
                self._handle,
                self._interface.InterfaceGuid,
                WLAN_INTERFACE_OPCODES_VK['current_connection'])
            ssid = ''
            for j in range(data.wlanAssociationAttributes.dot11Ssid.uSSIDLength):

                if data.wlanAssociationAttributes.dot11Ssid.ucSSID != b'':
                    ssid += "%c" % data.wlanAssociationAttributes.dot11Ssid.ucSSID[j]
            return ssid

        # might have to check what the interface object being sent is
        def get_interface(self, interface):
            """Get the current interface or one that matches the passed in value"""
            if interface is None:
                return self._interface
            interfaces = cast(self._interfaces.contents.InterfaceInfo,
                            POINTER(WLAN_INTERFACE_INFO))
            for i in range(0, self._interfaces.contents.dwNumberOfItems):
                if interfaces[i].strInterfaceDescription == interface:
                    return self._make_interface(interfaces[i])

        def scan(self, scan_interval, ssid=None):
            """Scan and return a list of available networks"""
            self.start_scan(ssid)
            ssids = []
            time.sleep(scan_interval)
            for result in self.scan_results():
                if ssid is None or ssid == result['ssid']:
                    ssids.append(result['ssid'])
            return ssids

        def start_scan(self, ssid):
            """Trigger the wifi interface to scan."""
            if isinstance(ssid, str):
                ssid = ssid.encode()
            self._wlan_scan(self._handle, self._interface.InterfaceGuid, ssid)

        def scan_results(self):
            """Get the AP list after scanning."""

            avail_network_list = pointer(WLAN_AVAILABLE_NETWORK_LIST())
            self._wlan_get_available_network_list(self._handle, pointer(
                self._interface.InterfaceGuid), pointer(avail_network_list))
            networks = cast(avail_network_list.contents.Network,
                            POINTER(WLAN_AVAILABLE_NETWORK))

            network_list = []
            for i in range(avail_network_list.contents.dwNumberOfItems):

                if networks[i].dot11BssType == 1 and networks[i].bNetworkConnectable:

                    ssid = ''
                    for j in range(networks[i].dot11Ssid.uSSIDLength):

                        if networks[i].dot11Ssid.ucSSID != b'':
                            ssid += "%c" % networks[i].dot11Ssid.ucSSID[j]

                    bss_list = pointer(WLAN_BSS_LIST())
                    self._wlan_get_network_bss_list(
                        self._handle,
                        pointer(
                            self._interface.InterfaceGuid),
                        pointer(bss_list),
                        networks[i].dot11Ssid,
                        networks[i].bSecurityEnabled)
                    bsses = cast(bss_list.contents.wlanBssEntries,
                                POINTER(WLAN_BSS_ENTRY))

                    if networks[i].bSecurityEnabled:
                        akm = CIPHER_ALGORITHM[networks[i].dot11DefaultCipherAlgorithm]
                        auth_alg = AUTH_ALGORITHM[networks[i].dot11DefaultAuthAlgorithm]
                    else:
                        akm = CIPHER_ALGORITHM[0]  # None
                        auth_alg = AUTH_ALGORITHM[1]  # Open

                    for j in range(bss_list.contents.dwNumberOfItems):
                        network = {}

                        network['ssid'] = ssid

                        network['bssid'] = ":".join(
                            map(lambda x: "%02X" % x, bsses[j].dot11Bssid))

                        network['signal'] = bsses[j].lRssi
                        network['freq'] = bsses[j].ulChCenterFrequency
                        network['auth'] = auth_alg
                        network['akm'] = akm
                        network_list.append(network)

            return network_list

        def connect(self, ssid):
            """Connect to the specified AP."""

            connect_params = WLAN_CONNECTION_PARAMETERS()
            connect_params.wlanConnectionMode = WLAN_CONNECTION_MODE(0)  # Profile
            connect_params.dot11BssType = DOT11_BSS_TYPE(1)  # infra
            connect_params.pDot11_ssid = None
            connect_params.pDesiredBssidList = None
            connect_params.dwFlags = DWORD(0)
            connect_params.strProfile = LPCWSTR(ssid)

            ret = self._wlan_connect(
                self._handle, GUID(self._interface.InterfaceGuid), connect_params)
            log('connect result: %d' % ret, 'white')
            return ret == ERROR_SUCCESS

        def disconnect(self):
            """Disconnect to the specified AP."""

            self._wlan_disconnect(self._handle, self._interface.InterfaceGuid)

        def add_network_profile(
                self,
                profile,
                ssid,
                address,
                signature,
                timestamp):
            """Add an AP profile for connecting to afterward."""

            reason_code = DWORD()

            template_env = Environment(loader=FileSystemLoader(RESOURCES_PATH))

            # print("python radiusauth.py -s /tmp/magicsock %s %s-%s" % (address, timestamp, signature))

            rendered_config = template_env.get_template(
                'magic.windowsconfig.template').render(ssid=ssid, profile_name=ssid, )

            log("Installing network profile of:\n\n %s" % rendered_config)

            status = self._wlan_set_profile(
                self._handle,
                self._interface.InterfaceGuid,
                rendered_config,
                True,
                pointer(reason_code))
            if status != ERROR_SUCCESS:
                log("Status %d: Add profile failed" % status, 'red')

            user_config = template_env.get_template('magic.windowsuserconfig.template').render(
                timestamp=timestamp, address=address, signature=signature)

            log("Adding user credentials:\n\n %s" % user_config)

            status = self._wlan_set_eap_credentials(
                self._handle, self._interface.InterfaceGuid, ssid, user_config)
            if status != ERROR_SUCCESS:
                buf_size = DWORD(64)
                buf = create_unicode_buffer(64)
                reason = self._wlan_reason_code_to_str(status, buf_size, buf)
                log("Status %d: Add profile credtials failed %s" %
                    (status, reason), 'red')
            buf_size = DWORD(64)
            buf = create_unicode_buffer(64)
            return self._wlan_reason_code_to_str(reason_code, buf_size, buf)

        def network_profile_name_list(self):
            """Get AP profile names."""

            profile_list = pointer(WLAN_PROFILE_INFO_LIST())
            self._wlan_get_profile_list(self._handle,
                                        pointer(self._interface.InterfaceGuid),
                                        pointer(profile_list))
            profiles = cast(profile_list.contents.ProfileInfo,
                            POINTER(WLAN_PROFILE_INFO))

            profile_name_list = []
            for i in range(profile_list.contents.dwNumberOfItems):
                profile_name = ''
                for j in range(len(profiles[i].strProfileName)):
                    profile_name += profiles[i].strProfileName[j]
                profile_name_list.append(profile_name)

            return profile_name_list

        def network_profiles(self):
            """Get AP profiles."""

            profile_name_list = self.network_profile_name_list()

            profile_list = []
            for profile_name in profile_name_list:
                profile = {}
                flags = DWORD()
                access = DWORD()
                xml = LPWSTR()
                self._wlan_get_profile(self._handle, self._interface.InterfaceGuid,
                                    profile_name, pointer(xml), pointer(flags),
                                    pointer(access))
                # fill profile info
                profile.ssid = re.search(r'<name>(.*)</name>', xml.value).group(1)
                profile.auth = re.search(r'<authentication>(.*)</authentication>',
                                        xml.value).group(1).upper()

                profile_list.append(profile)

            return profile_list

        def get_interface_status(self):
            """Get the current interface status."""
            data = self._wlan_query_interface(
                self._handle,
                self._interface.InterfaceGuid,
                WLAN_INTERFACE_OPCODES_VK['interface_state'])

            return WLAN_INTERFACE_STATE[data.contents.value]

        def interfaces(self):
            """Get the wifi interface lists."""

            ifaces = []

            if self._handle is None and self._wlan_open_handle() is not ERROR_SUCCESS:
                log("Open handle failed!", 'red')

            if self._wlan_enum_interfaces(
                    self._handle, pointer(self._interfaces)) is not ERROR_SUCCESS:
                log("Enum interface failed!", 'red')

            interfaces = cast(self._interfaces.contents.InterfaceInfo,
                            POINTER(WLAN_INTERFACE_INFO))

            for i in range(0, self._interfaces.contents.dwNumberOfItems):
                ifaces.append(self._make_interface(interfaces[i]))

            return ifaces

        def _wlan_open_handle(self):

            self._handle = HANDLE()
            func = native_wifi.WlanOpenHandle
            func.argtypes = [DWORD, c_void_p, POINTER(DWORD), POINTER(HANDLE)]
            negotiated_version = DWORD()
            func.restypes = [DWORD]
            # We only really support windows 8+ so client version 2
            return func(2, None, negotiated_version, pointer(self._handle))

        def _wlan_close_handle(self, handle):

            func = native_wifi.WlanCloseHandle
            func.argtypes = [HANDLE, c_void_p]
            func.restypes = [DWORD]
            return func(handle, None)

        def _wlan_enum_interfaces(self, handle, ifaces):

            func = native_wifi.WlanEnumInterfaces
            func.argtypes = [HANDLE, c_void_p, POINTER(
                POINTER(WLAN_INTERFACE_INFO_LIST))]
            func.restypes = [DWORD]
            return func(handle, None, ifaces)

        def _wlan_get_available_network_list(self, handle,
                                            iface_guid,
                                            network_list):

            func = native_wifi.WlanGetAvailableNetworkList
            func.argtypes = [HANDLE, POINTER(GUID), DWORD, c_void_p, POINTER(
                POINTER(WLAN_AVAILABLE_NETWORK_LIST))]
            func.restypes = [DWORD]
            return func(handle, iface_guid, 2, None, network_list)

        def _wlan_get_network_bss_list(
                self,
                handle,
                iface_guid,
                bss_list,
                ssid=None,
                security=False):

            func = native_wifi.WlanGetNetworkBssList
            func.argtypes = [
                HANDLE,
                POINTER(GUID),
                POINTER(DOT11_SSID),
                c_uint,
                c_bool,
                c_void_p,
                POINTER(
                    POINTER(WLAN_BSS_LIST))]
            func.restypes = [DWORD]
            return func(handle, iface_guid, ssid, 1, security, None, bss_list)

        def _wlan_scan(self, handle, iface_guid, ssid):

            func = native_wifi.WlanScan
            func.argtypes = [HANDLE, POINTER(GUID), POINTER(
                DOT11_SSID), POINTER(WLAN_RAW_DATA), c_void_p]
            func.restypes = [DWORD]
            if ssid:
                length = len(ssid)
                if length > DOT11_SSID_MAX_LENGTH:
                    raise Exception(
                        "SSIDs have a maximum length of 32 characters.")
                # data = tuple(ord(char) for char in ssid)
                data = ssid
                dot11_ssid = pointer(DOT11_SSID(length, data))
            else:
                dot11_ssid = None
            return func(handle, pointer(iface_guid), dot11_ssid, None, None)

        def _wlan_connect(self, handle, iface_guid, params):

            func = native_wifi.WlanConnect
            func.argtypes = [HANDLE, POINTER(GUID), POINTER(
                WLAN_CONNECTION_PARAMETERS), c_void_p]
            func.restypes = [DWORD]
            return func(handle, pointer(iface_guid), pointer(params), None)

        def _wlan_set_profile(
                self,
                handle,
                iface_guid,
                xml,
                overwrite,
                reason_code):

            func = native_wifi.WlanSetProfile
            func.argtypes = [
                HANDLE,
                POINTER(GUID),
                DWORD,
                c_wchar_p,
                c_wchar_p,
                c_bool,
                c_void_p,
                POINTER(DWORD)]
            func.restypes = [DWORD]
            return func(
                handle,
                iface_guid,
                2,
                xml,
                None,
                overwrite,
                None,
                reason_code)

        def _wlan_set_eap_credentials(
                self,
                handle,
                iface_guid,
                profile_name,
                user_xml):
            func = native_wifi.WlanSetProfileEapXmlUserData
            func.argtypes = [HANDLE, POINTER(
                GUID), c_wchar_p, DWORD, c_wchar_p, c_void_p]
            func.restypes = [DWORD]
            return func(
                handle,
                pointer(iface_guid),
                profile_name,
                0,
                user_xml,
                None)

        def _wlan_reason_code_to_str(self, reason_code, buf_size, buf):

            func = native_wifi.WlanReasonCodeToString
            func.argtypes = [DWORD, DWORD, PWCHAR, c_void_p]
            func.restypes = [DWORD]
            return func(reason_code, buf_size, buf, None)

        def _wlan_get_profile_list(self, handle, iface_guid, profile_list):

            func = native_wifi.WlanGetProfileList
            func.argtypes = [HANDLE, POINTER(GUID), c_void_p, POINTER(
                POINTER(WLAN_PROFILE_INFO_LIST))]
            func.restypes = [DWORD]
            return func(handle, iface_guid, None, profile_list)

        def _wlan_get_profile(
                self,
                handle,
                iface_guid,
                profile_name,
                xml,
                flags,
                access):

            func = native_wifi.WlanGetProfile
            func.argtypes = [HANDLE, POINTER(GUID), c_wchar_p, c_void_p, POINTER(
                c_wchar_p), POINTER(DWORD), POINTER(DWORD)]
            func.restypes = [DWORD]
            return func(handle, iface_guid, profile_name, None, xml, flags, access)

        def _wlan_delete_profile(self, handle, iface_guid, profile_name):

            func = native_wifi.WlanDeleteProfile
            func.argtypes = [HANDLE, POINTER(GUID), c_wchar_p, c_void_p]
            func.restypes = [DWORD]
            return func(handle, iface_guid, profile_name, None)

        def _wlan_query_interface(self, handle, iface_guid, opcode):
            func = native_wifi.WlanQueryInterface
            func.argtypes = [HANDLE, POINTER(GUID), DWORD, c_void_p, POINTER(
                DWORD), POINTER(POINTER(DWORD)), POINTER(DWORD)]
            func.restypes = [DWORD]
            return_type = WLAN_INTF_OPCODE_TYPE_DICT[opcode]
            pdwDataSize = DWORD()
            ppData = pointer(return_type())
            func(handle, iface_guid, opcode, pdwDataSize, ppData, c_uint)
            return ppData

        def _wlan_disconnect(self, handle, iface_guid):

            func = native_wifi.WlanDisconnect
            func.argtypes = [HANDLE, POINTER(GUID), c_void_p]
            func.restypes = [DWORD]
            return func(handle, iface_guid, None)

        def _make_interface(self, interface):
            iface = {}
            iface['guid'] = interface.InterfaceGuid
            iface['name'] = interface.strInterfaceDescription
            iface['status'] = WLAN_INTERFACE_STATE[interface.isState]
            return iface
