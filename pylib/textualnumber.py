class TextualNumber:
    """Convert numbers to English words (same logic as PHP version)."""

    ONES = ["", "One", "Two", "Three", "Four", "Five", "Six",
            "Seven", "Eight", "Nine", "Ten", "Eleven", "Twelve",
            "Thirteen", "Fourteen", "Fifteen", "Sixteen", "Seventeen",
            "Eighteen", "Nineteen"]
    TENS = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty",
            "Seventy", "Eighty", "Ninety"]

    def __init__(self, string=None):
        self.data = []
        if string is not None:
            for value in str(string).split(','):
                parts = value.split('.')
                rs = "Rupees " + self.num_to_words(int(parts[0]))
                ps = ""
                if len(parts) == 2 and parts[1]:
                    ps = " and " + self.num_to_words(int(parts[1])) + " Paise"
                self.data.append(rs + ps)

    def num_to_words(self, number):
        if number < 0 or number > 999999999:
            return f"{number} out of script range"

        lakhs = number // 100000
        number %= 100000
        thousands = number // 1000
        number %= 1000
        hundreds = number // 100
        number %= 100
        tens = number // 10
        ones = number % 10
        res = ""

        if lakhs:
            res += self.num_to_words(lakhs) + " hundred"
        if thousands:
            res += ("" if not res else " ") + self.num_to_words(thousands) + " Thousand"
        if hundreds:
            res += ("" if not res else " ") + self.num_to_words(hundreds) + " Hundred"
        if tens or ones:
            if res:
                res += " and "
            if tens < 2:
                res += self.ONES[tens * 10 + ones]
            else:
                res += self.TENS[tens]
                if ones:
                    res += "-" + self.ONES[ones]
        return res if res else "zero"
