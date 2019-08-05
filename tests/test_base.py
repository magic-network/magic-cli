from magic.daemon.network_monitor import NetworkMonitor
from magic.account.account_manager import AccountManager
from magic.network.network_manager import NetworkManager
from magic.wireless.wireless import Wireless

def test_80211x_creds():
    wireless = Wireless()
    account_manager = AccountManager(wireless)
    account_manager.setup_8021x_creds('test')

def test_network():
    wireless = Wireless()
    network_manager = NetworkManager(wireless)