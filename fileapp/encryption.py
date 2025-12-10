import os
import base64
import hashlib
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.fernet import Fernet
from django.conf import settings

def _wrapper_fernet():
    key = hashlib.sha256(settings.SECRET_KEY.encode()).digest()
    return Fernet(base64.urlsafe_b64encode(key))

def generate_aes_key():
    return AESGCM.generate_key(bit_length=256)

def encrypt_bytes(plain_bytes):
    key = generate_aes_key()
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ct = aesgcm.encrypt(nonce, plain_bytes, None)
    wrapped = _wrapper_fernet().encrypt(key)
    payload = nonce + ct
    return payload, base64.b64encode(wrapped).decode()

def decrypt_bytes(payload, wrapped_b64):
    wrapped = base64.b64decode(wrapped_b64)
    key = _wrapper_fernet().decrypt(wrapped)
    nonce = payload[:12]
    ct = payload[12:]
    aesgcm = AESGCM(key)
    pt = aesgcm.decrypt(nonce, ct, None)
    return pt
