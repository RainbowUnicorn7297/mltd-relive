import gzip
from base64 import b64decode, b64encode

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

_key = b'do8PxbqYKV7cexTrt4J3fmgBtXXzu+dP'
_iv = b'\x00' * 16


def decrypt_request(data):
    cipher = AES.new(_key, AES.MODE_CBC, iv=_iv)
    data = unpad(cipher.decrypt(b64decode(data, b'-_')), 16)
    return bytearray(data)[16:]


def decrypt_response(data):
    cipher = AES.new(_key, AES.MODE_CBC, iv=_iv)
    data = unpad(cipher.decrypt(b64decode(data, b'-_')), 16)
    return gzip.decompress(bytearray(data)[16:])


def encrypt_response(data):
    cipher = AES.new(_key, AES.MODE_CBC, iv=_iv)
    data = b'\x00' * 16 + gzip.compress(bytes(data, 'UTF-8'))
    return b64encode(cipher.encrypt(pad(data, 16)), b'-_')

