from builtins import bytes
import ecdsa
import sha3
import six

from eth_utils.address import decode_hex
from eth_keys import keys

def encode_hex_string(data):
    return ''.join('{:02X}'.format(x) for x in six.iterbytes(data))

# Generate a new ethereum account
def generate_account():
    priv = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
    pub = priv.get_verifying_key().to_string()

    keccak = sha3.keccak_256()
    keccak.update(pub)
    address = keccak.hexdigest()[24:]

    return type('obj', (object,), {
        'pubkey': encode_hex_string(pub),
        'address': checksum_encode(address),
        'privkey': encode_hex_string(priv.to_string())
    })


def checksum_encode(addr_str):
    keccak_256 = sha3.keccak_256()
    out = ''
    addr = addr_str.lower().replace('0x', '')
    keccak_256.update(addr.encode('ascii'))
    hash_addr = keccak_256.hexdigest()

    for i, c in enumerate(addr):
        if int(hash_addr[i], 16) >= 8:
            out += c.upper()
        else:
            out += c

    return '0x' + out


def get_pub_from_privkey(private_key):
    return keys.private_key_to_public_key(keys.PrivateKey(decode_hex(private_key))).to_address()


def sign(message, private_key):
    # Hash the agreed upon message
    message_hash = sha3.keccak_256(bytes(message, 'utf8')).digest()
    # Convert private key to binary
    priv_key = decode_hex(private_key)
    # Sign with private key
    signature = keys.ecdsa_sign(message_hash, keys.PrivateKey(priv_key))
    # Assign recovery bit used to recover the public key of the transaction signer
    vrs = signature.vrs
    vrs_list = list(vrs)
    vrs_list[0] = vrs_list[0] + 27
    # Stringify signature for transport
    stringified_sig = '-'.join(str(x) for x in vrs_list)

    return stringified_sig
