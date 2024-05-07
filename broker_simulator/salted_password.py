import bcrypt


class SaltedPassword:
    def __init__(self, password: str):
        self.password: str = password

        self.salt: str = bcrypt.gensalt().decode()

        password_bytes = self.password.encode()
        password_hashed_bytes: bytes = bcrypt.hashpw(password_bytes, self.salt.encode())

        self.password_hash = password_hashed_bytes.decode()

    @staticmethod
    def check_password(password_to_check: str, stored_password_hash: str, salt: str) -> bool:
        password_to_check_bytes = password_to_check.encode()
        salt_bytes = salt.encode()
        hashed_password_to_check = bcrypt.hashpw(password_to_check_bytes, salt_bytes)
        return hashed_password_to_check == stored_password_hash.encode()
