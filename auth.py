import hashlib

SALT = "34653hfrfjkdf*###M@DMS23"


def hash_password(password: str):
    password = f"{password}{SALT}"
    password = password.encode()
    return str(hashlib.md5(password))
