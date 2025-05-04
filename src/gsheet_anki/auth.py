import binascii
import hashlib
import os

from flask_httpauth import HTTPBasicAuth

auth = HTTPBasicAuth()

# Load username and password from environment variables
USER_DATA = {
    os.getenv("USERNAME", "admin"): os.getenv("PASSWORD_HASH", "527c6c91188a9d4399666dd335b9bfce$4c19590f90adde028ffb20f49dfd4f6ce8f90262199617452847cd1538ec97719dd0bd1066f22853f3537947f39fed171b7c0ea46d4d4946008ada6e00297a2a")
}


@auth.verify_password
def verify_password(username, password):
    if username in USER_DATA:
        stored_password_hash = USER_DATA[username]
        if stored_password_hash:
            salt, stored_hash = stored_password_hash.split('$')
            hashed_password = hashlib.scrypt(
                password.encode('utf-8'),
                salt=binascii.unhexlify(salt),
                n=16384,
                r=8,
                p=1
            )
            if binascii.hexlify(hashed_password).decode('utf-8') == stored_hash:
                return username
    return None


def hash_password(password):
    salt = os.urandom(16)
    hashed_password = hashlib.scrypt(
        password.encode('utf-8'),
        salt=salt,
        n=16384,
        r=8,
        p=1
    )
    return f"{binascii.hexlify(salt).decode('utf-8')}${binascii.hexlify(hashed_password).decode('utf-8')}"
