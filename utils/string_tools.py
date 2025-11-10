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

    @staticmethod
    def contains_persian(text: str) -> bool:
        pattern = re.compile(r'[\u0600-\u06FF]')
        return bool(pattern.search(text))

    @staticmethod
    def is_valid_shaba(sheba: str) -> bool:
        pattern = r'^[0-9]{24}$'
        return bool(re.fullmatch(pattern, sheba.strip()))

    @staticmethod
    def is_valid_card_number(card: str) -> bool:
        pattern_plain = re.compile(r'^\d{16}$')
        pattern_spaced = re.compile(r'^(?:\d{4}[ -]?){3}\d{4}$')
        s = card.strip()
        return bool(pattern_plain.fullmatch(s) or pattern_spaced.fullmatch(s))

    @staticmethod
    def is_trx_address(address: str) -> bool:
        address = address.strip()
        pattern = r'^T[1-9A-HJ-NP-Za-km-z]{33}$'
        return bool(re.match(pattern, address))

    @staticmethod
    def is_valid_trx_private_key(s: str) -> bool:
        regex = re.compile(r'^(?:0x)?[0-9a-fA-F]{64}$')
        return bool(regex.match(s))

class Password:

    @staticmethod
    def generate_password() -> str:
        length: int = 12

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


class Text:

    @staticmethod
    def number_to_emoji(number: int) -> str:
        emoji_list = {0: "0️⃣", 1: "1️⃣", 2: "2️⃣", 3: "3️⃣", 4: "4️⃣", 5: "5️⃣", 6: "6️⃣", 7: "7️⃣", 8: "8️⃣", 9: "9️⃣"}
        number = str(number)

        for n in number:
            for num, emoji in emoji_list.items():
                if n == str(num):
                    number = number.replace(n, emoji)

        return number
