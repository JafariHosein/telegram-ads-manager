

class NumberTools:

    @staticmethod
    def format_number(number):
        return "{:,}".format(int(number))

    @staticmethod
    def unformat_number(number):
        return int(number.replace(",", ""))

    @staticmethod
    def number_to_words(num):
        ones = ["", "یک", "دو", "سه", "چهار", "پنج", "شش", "هفت", "هشت", "نه"]
        tens = ["", "ده", "بیست", "سی", "چهل", "پنجاه", "شصت", "هفتاد", "هشتاد", "نود"]
        teens = ["ده", "یازده", "دوازده", "سیزده", "چهارده", "پانزده", "شانزده", "هفده", "هجده", "نوزده"]
        hundreds = ["", "صد", "دویست", "سیصد", "چهارصد", "پانصد", "ششصد", "هفتصد", "هشتصد", "نهصد"]
        thousands = ["", "هزار", "میلیون", "میلیارد"]

        def three_digit_to_words(n):
            h = n // 100
            t = (n % 100) // 10
            o = n % 10
            words = []
            if h > 0:
                words.append(hundreds[h])
            if t == 1:
                words.append(teens[o])
            else:
                if t > 1:
                    words.append(tens[t])
                if o > 0:
                    words.append(ones[o])
            return " و ".join(words)

        if num == 0:
            return "صفر تومان"

        parts = []
        i = 0
        while num > 0:
            n = num % 1000
            if n != 0:
                part = three_digit_to_words(n)
                if thousands[i]:
                    part += " " + thousands[i]
                parts.append(part)
            num //= 1000
            i += 1

        parts.reverse()
        result = " و ".join(parts)
        return result + " تومان"

    @staticmethod
    def words_to_number(text):
        units = {
            "صفر": 0, "یک": 1, "دو": 2, "سه": 3, "چهار": 4, "پنج": 5, "شش": 6, "هفت": 7, "هشت": 8, "نه": 9,
            "ده": 10, "یازده": 11, "دوازده": 12, "سیزده": 13, "چهارده": 14, "پانزده": 15, "شانزده": 16,
            "هفده": 17, "هجده": 18, "نوزده": 19, "بیست": 20, "سی": 30, "چهل": 40, "پنجاه": 50, "شصت": 60,
            "هفتاد": 70, "هشتاد": 80, "نود": 90, "صد": 100, "دویست": 200, "سیصد": 300, "چهارصد": 400,
            "پانصد": 500, "ششصد": 600, "هفتصد": 700, "هشتصد": 800, "نهصد": 900
        }
        multiples = {
            "هزار": 1000,
            "میلیون": 1000000,
            "میلیارد": 1000000000
        }

        text = text.replace("تومان", "").strip()
        words = text.split()

        total = 0
        current = 0
        last_multiplier = 1

        for w in words:
            if w == "و":
                continue
            elif w in units:
                current += units[w]
            elif w in multiples:
                if current == 0:
                    current = 1
                current *= multiples[w]
                total += current
                current = 0
            else:
                pass

        total += current
        return total