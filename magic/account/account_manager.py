import time
from magic.util.log import log
from magic.util.prompt import get_prompt
from magic.util.eth import generate_account, sign
from magic.wireless.wireless import Wireless

class AccountManager:
    def __init__(self, channel_manager):

        self.channel_manager = channel_manager
        self.onboarded = False
        self.address = None
        self.privkey = None
        self.wireless = Wireless()

    def get_user(self):

        answers = get_prompt([
            {
                'type': 'list',
                'name': 'onboard_account_choice',
                'message': 'Ethereum Setup:',
                'choices': [
                    {
                        "name": "Create a new test Ethereum account",
                        "value": "new_account"
                    },
                    {
                        "name": "Enter existing test account using your test private key.",
                        "value": "existing_account"
                    },
                    {
                        "name": "Exit Magic CLI",
                        "value": "graceful_exit"
                    }
                ]
            }, {
                'type': 'password',
                'name': 'eth_privkey',
                'when': lambda answers: answers['onboard_account_choice'] == "existing_account",
                'message': 'Enter private key'
            }])

        try:

            if answers['onboard_account_choice'] == "new_account":
                self.create_eth_account()

            if answers['onboard_account_choice'] == "existing_account":
                self.privkey = answers['eth_privkey']

            if answers['onboard_account_choice'] == "graceful_exit":
                log('Goodbye!', 'green')
                exit()

            self.onboarded = True

        except KeyError:
            log('Goodbye!', 'green')
            exit()

    def get_eth_account(self, priv_key):

        self.privkey = priv_key
        self.pubkey = "0x" + get_pub_from_privkey(priv_key).lower()

        log("Address: %s" % self.address, "blue")
        log("Private key: %s" % self.privkey, "blue")

    def create_eth_account(self):

        account = generate_account()

        self.address = account.address
        self.privkey = account.privkey

        log("Address: %s" % self.address, "blue")
        log("Private key: %s" % self.privkey, "blue")

        self.channel_manager.create_process(self.address, self.privkey, 100000)



    def setup_8021x_creds(self, ssid):
        has_creds = self.wireless.has_8021x_creds(ssid, self.address, self.privkey)

        if has_creds is False:
            timestamp = str(int(time.time()))

            self.wireless.install_8021x_creds(
                ssid,
                self.address,
                sign("auth_" + timestamp, self.privkey),
                timestamp
            )
