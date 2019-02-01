from web3 import Web3
import os
import requests
import json
import time
from magic.util.eth import sign

class ChannelManager:

    def __init__(self):

        self.web3_provider = Web3.HTTPProvider("https://rinkeby.infura.io/50686e66f0c143dc968ee9ab73a726a8")
        self.web3 = Web3(self.web3_provider)
        self.load_contracts()

    def load_contracts(self):

        this_dir, this_filename = os.path.split(__file__)

        token_abi_path = os.path.join(this_dir, "..", "resources", "MagicToken.json")
        faucet_abi_path = os.path.join(this_dir, "..", "resources", "MagicTokenFaucet.json")
        channel_abi_path = os.path.join(this_dir, "..", "resources", "MagicChannels.json")

        self.token_addr = Web3.toChecksumAddress("0xc3cbfd0d0f583987ea43d92f7bc2624052ffd6f5")
        self.faucet_addr = Web3.toChecksumAddress("0x7ca9360a59737e5bf3611b1877db8abe292db033")
        self.channel_addr = Web3.toChecksumAddress("0x0df70c960542cf3bc879772fb84e24ea614024b5")
        self.payment_enabler_addr = Web3.toChecksumAddress("0x18789511134a4c211C4a0E9661f868102C5DaBd7")

        with open(token_abi_path) as f:
            token_abi = json.load(f)

        with open(faucet_abi_path) as f:
            faucet_abi = json.load(f)

        with open(channel_abi_path) as f:
            channel_abi = json.load(f)

        self.token_contract = self.web3.eth.contract(address=self.token_addr, abi=token_abi["abi"])
        self.faucet_contract = self.web3.eth.contract(address=self.faucet_addr, abi=faucet_abi["abi"])
        self.channel_contract = self.web3.eth.contract(address=self.channel_addr, abi=channel_abi["abi"])

    def get_airdropped(self, address, priv_key):

        body = {
            "address": address,
            "sig": sign("it's me!", priv_key)
        }

        print("Airdropping...")
        r = requests.post('http://127.0.0.1:5000/airdrop', data=json.dumps(body))

        has_tokens = False
        has_eth = False

        while not has_eth:
            eth_balance = self.web3.eth.getBalance(address)
            has_eth = eth_balance > 0
            if not has_eth:
                print("Still airdropping...")
                time.sleep(2)

        # Poll here for those sweet sweet tokens.
        while not has_tokens:
            mgc_tokens = self.token_contract.functions.balanceOf(address).call()
            has_tokens = mgc_tokens > 0
            if not has_tokens:
                print("Still airdropping...")
                time.sleep(2)

        print("Airdrop complete: %s ETH, %s MGC" % (eth_balance, mgc_tokens))

    def approve_channel(self, address, priv_key, escrow):
        print("Approving creation of new channel...")

        approve_tx = self.token_contract.functions.approve(self.channel_addr, escrow).buildTransaction({
            'chainId': 4,   # Rinkeby for now.
            'gas': 70000,
            'gasPrice': Web3.toWei('1', 'gwei'),
            'nonce': self.web3.eth.getTransactionCount(address)
        })

        signed_tx = self.web3.eth.account.signTransaction(approve_tx, private_key=priv_key)
        self.web3.eth.sendRawTransaction(signed_tx.rawTransaction)

        is_approved = False

        # Poll here for those sweet sweet approval tokens.
        while not is_approved:
            mgc_approved = self.token_contract.functions.allowance(address, self.channel_addr).call()
            is_approved = mgc_approved > 0
            if not is_approved:
                print("Still Approving...")
                time.sleep(2)

        print("Channel creation approved.")

    def create_channel(self, address, priv_key, escrow):

        print("Creating new channel...")

        create_tx = self.channel_contract.functions.createChannel(self.payment_enabler_addr, escrow).buildTransaction({
            'chainId': 4,   # Rinkeby for now.
            'gas': 600000,
            'gasPrice': Web3.toWei('1', 'gwei'),
            'nonce': self.web3.eth.getTransactionCount(address)
        })

        signed_tx = self.web3.eth.account.signTransaction(create_tx, private_key=priv_key)
        self.web3.eth.sendRawTransaction(signed_tx.rawTransaction)

        is_created = False
        while not is_created:
            channel_amount = self.channel_contract.functions.myUserBalance(self.payment_enabler_addr).call()
            print(channel_amount)
            is_created = channel_amount > 0
            if not is_created:
                print("Still creating...")
                time.sleep(2)

        print("New channel created.")

    def create_process(self, address, priv_key, escrow):
        self.get_airdropped(address, priv_key)
        self.approve_channel(address, priv_key, escrow)
        self.create_channel(address, priv_key, escrow)




