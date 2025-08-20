from bcrypt import (
    gensalt as bcrypt_gensalt,
    hashpw as bcrypt_hashpw,
    checkpw as bcrypt_checkpw,
)


def hash_password(password: str) -> bytes:
    random_salt: bytes = bcrypt_gensalt()
    bytes_password: bytes = password.encode()

    return bcrypt_hashpw(password=bytes_password, salt=random_salt)


def check_password(password: str, hashed_password: bytes) -> bool:
    return bcrypt_checkpw(
        password=password.encode(),
        hashed_password=hashed_password,
    )
