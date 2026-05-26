import os
import base64
import hashlib
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def _get_key() -> bytes:
    key = os.getenv("ENCRYPTION_KEY")
    if not key:
        raise ValueError("ENCRYPTION_KEY nicht gesetzt")
    return hashlib.sha256(key.encode()).digest()

def encrypt(value: str) -> str:
    key = _get_key()
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    encrypted = aesgcm.encrypt(nonce, value.encode(), None)
    return base64.urlsafe_b64encode(nonce + encrypted).decode()

def decrypt(value: str) -> str:
    key = _get_key()
    aesgcm = AESGCM(key)
    data = base64.urlsafe_b64decode(value.encode())
    nonce = data[:12]
    encrypted = data[12:]
    return aesgcm.decrypt(nonce, encrypted, None).decode()

def hash_api_key(api_key: str) -> str:
    return hashlib.sha512(api_key.encode()).hexdigest()

def verify_api_key(api_key: str, stored_hash: str) -> bool:
    return hash_api_key(api_key) == stored_hash

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, stored_hash: str) -> bool:
    return pwd_context.verify(password, stored_hash)