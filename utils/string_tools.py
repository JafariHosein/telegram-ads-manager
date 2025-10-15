import re
import string
import secrets
import random
import bcrypt


class Regex:

    @staticmethod
    def is_username(text: str) -> bool:
        pattern = r"^@[A-Za-z][A-Za-z0-9_]{4,31}$"
        return bool(re.match(pattern, text))

    @staticmethod
    def contains_exact(text: str, target: str) -> bool:
        pattern = rf"(?<![A-Za-z0-9_]){re.escape(target)}(?![A-Za-z0-9_])"
        return re.search(pattern, text) is not None

    @staticmethod
    def is_prize_text(text: str) -> bool:
        pattern = re.compile(r'^(?:(?:[1-9]|10)\s*->\s*\d+\s*(?:\r?\n|$)){1,10}$')
        return bool(pattern.fullmatch(text.strip()))


class Password:

    @staticmethod
    def generate_password() -> str:
        length: int = 8

        lower = string.ascii_lowercase
        upper = string.ascii_uppercase
        digits = string.digits

        password_chars = [
            secrets.choice(lower),
            secrets.choice(upper),
            secrets.choice(digits)
        ]

        all_chars = lower + upper + digits

        for _ in range(length - 4):
            password_chars.append(secrets.choice(all_chars))

        random.SystemRandom().shuffle(password_chars)

        return "".join(password_chars)

    @staticmethod
    def hash_password(password: str) -> str:
        password_bytes = password.encode("utf-8")

        hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())

        return hashed.decode("utf-8")
