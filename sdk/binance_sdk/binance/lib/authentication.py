import hmac
import hashlib
from base64 import b64encode
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto.Signature import PKCS1_v1_5


def hmac_hashing(api_secret, payload):
    """哈希签名"""
    m = hmac.new(api_secret.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256)
    return m.hexdigest()


def rsa_signature(private_key, payload, private_key_pass=None):
    """rsa签名"""
    private_key = RSA.import_key(private_key, passphrase=private_key_pass)
    h = SHA256.new(payload.encode("utf-8"))
    signature = PKCS1_v1_5.new(private_key).sign(h)
    return b64encode(signature)
