from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from base64 import b64encode, b64decode
import gzip, json

key = b'do8PxbqYKV7cexTrt4J3fmgBtXXzu+dP'
iv = b'\x00' * 16

def decrypt_response(data):
    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    data = unpad(cipher.decrypt(b64decode(data, b'-_')), 16)
    data = gzip.decompress(bytearray(data)[16:])
    return json.loads(data)

def encrypt_response(data):
    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    data = json.dumps(data, separators=(',', ':'))
    data = b'\x00' * 16 + gzip.compress(bytes(data, 'UTF-8'))
    return b64encode(cipher.encrypt(pad(data, 16)), b'-_')
