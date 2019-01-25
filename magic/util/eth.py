import os
from web3.auto import w3
from ethereum.utils import privtoaddr, encode_hex, decode_hex, ecsign, sha3, normalize_key, ecrecover_to_pub, checksum_encode

# Generate a new ethereum account
def generate_account():

    acct = w3.eth.account.create(os.urandom(4096))
    priv = acct.privateKey
    address = acct.address
    priv_hex = priv.hex()

    return type('obj', (object,), {
        'address': address,
        'privkey': priv_hex,
    })

def sign(message, key):
    msg_hash = sha3(message)
    sig_object = w3.eth.account.signHash(msg_hash, private_key=key)
    return sig_object.signature.hex()

def verify_sig(message, signature, address):
    msg_hash = sha3(message)
    recovered_address = w3.eth.account.recoverHash(msg_hash, signature=signature)
    return address == recovered_address

def pubtoaddr(pub):
    return encode_hex(sha3(pub)[-20:])