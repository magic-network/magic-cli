from web3 import Web3
import requests
import json

class ChannelManager:

    def __init__(self):
        self.web3_provider = Web3.HTTPProvider("https://rinkeby.infura.io/50686e66f0c143dc968ee9ab73a726a8")
        self.load_contracts()

    def load_contracts(self):

        token_abi_path = ""
        faucet_abi_path = ""

        with open(token_abi_path) as f:
            token_abi = json.load(f)

        with open(faucet_abi_path) as f:
            faucet_abi = json.load(f)

        self.token_contract = self.web3.eth.contract(address=self.mgc_contract_address, abi=token_abi["abi"])
        self.faucet_contract = self.web3.eth.contract(address=self.mgc_contract_address, abi=faucet_abi["abi"])

    def get_airdropped(self, address, priv_key):

        nonce = self.app.web3.eth.getTransactionCount(address)

        request_tx = self.faucet_contract.functions.request().buildTransaction({
            'chainId': 4,
            'gas': 70000,
            'gasPrice': self.app.web3.toWei('1', 'gwei'),
            'nonce': nonce
        })

        signed_request_tx = self.app.web3.eth.account.signTransaction(request_tx, private_key=priv_key)

        headers = {
            'user_addr': address,
            'user_privkey': priv_key,
            'Content-Type': 'application/json'
        }

        body = {
            "escrow": 10000
        }

        r = requests.post('http://127.0.0.1:5000/airdrop', headers=headers, data=json.dumps(body))

        print(r.status_code)

    def approve_channel(self):

        nonce = self.app.web3.eth.getTransactionCount(address)

        request_tx = self.token_contract.functions.request().buildTransaction({
            'chainId': 4,
            'gas': 70000,
            'gasPrice': self.app.web3.toWei('1', 'gwei'),
            'nonce': nonce
        })

        signed_request_tx = self.app.web3.eth.account.signTransaction(request_tx, private_key=priv_key)

        headers = {
            'user_addr': address,
            'user_privkey': priv_key,
            'Content-Type': 'application/json'
        }

        body = {
            "escrow": 10000
        }

        r = requests.post('http://127.0.0.1:5000/channel', headers=headers, data=json.dumps(body))

        print(r.status_code)

    def create_channel(self, escrow):

        nonce = self.app.web3.eth.getTransactionCount(address)

        request_tx = self.token_faucet_contract.functions.request().buildTransaction({
            'chainId': 4,
            'gas': 70000,
            'gasPrice': self.app.web3.toWei('1', 'gwei'),
            'nonce': nonce
        })

        signed_request_tx = self.app.web3.eth.account.signTransaction(request_tx, private_key=priv_key)

        headers = {
            'user_addr': address,
            'user_privkey': priv_key,
            'Content-Type': 'application/json'
        }

        body = {
            "escrow": 10000
        }

        r = requests.post('http://127.0.0.1:5000/channel', headers=headers, data=json.dumps(body))

        print(r.status_code)

    def create_process(self, address, priv_key, escrow):

        self.get_airdropped(address, priv_key)
        self.approve_channel(address, priv_key)
        self.create_channel(address, priv_key, escrow)

        pass




