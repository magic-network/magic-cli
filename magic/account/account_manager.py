import time
from magic.util.log import log
from magic.util.prompt import get_prompt
from magic.util.eth import generate_account, get_pub_from_privkey, sign
from magic.wireless.wireless import Wireless


class AccountManager:
    def __init__(self):
        self.onboarded = False
        self.pubkey = None
        self.address = None
        self.privkey = None
        self.wireless = Wireless()

    def get_critical_info(self):
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
                account = generate_account()
                self.pubkey = account.pubkey.lower()
                self.address = account.address.lower()
                self.privkey = account.privkey.lower()
                log("Your new public key: %s" % self.pubkey, "blue")
                log("Your new address: %s" % self.address, "blue")
                log("Your new private key: %s" % self.privkey, "blue")

            if answers['onboard_account_choice'] == "existing_account":
                self.privkey = answers['eth_privkey']
                self.pubkey = "0x" + get_pub_from_privkey(self.privkey).lower()

            if answers['onboard_account_choice'] == "graceful_exit":
                log('Goodbye!', 'green')
                exit()

            self.onboarded = True

        except KeyboardInterrupt:
            log('Goodbye!', 'green')
            exit()

    def setup_8021x_creds(self, ssid):
        has_creds = self.wireless.has_8021x_creds(ssid, self.pubkey, self.privkey)

        if has_creds is False:
            timestamp = str(int(time.time()))

            self.wireless.install_8021x_creds(
                ssid,
                self.pubkey,
                sign("auth_" + timestamp, self.privkey),
                timestamp
            )
