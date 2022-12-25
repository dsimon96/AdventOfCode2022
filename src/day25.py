from collections import deque
from typing import TextIO

BASE = 5


def decode_digit(c: str) -> int:
    if c.isdigit():
        return int(c)
    elif c == "-":
        return -1
    else:
        return -2


def encode_digit(digit: int) -> str:
    if digit >= 0:
        return str(digit)
    elif digit == -1:
        return "-"
    else:
        return "="


class SnafuCodedInt:
    digits = deque[int]()

    def __init__(self, val: int | str):
        if isinstance(val, str):
            self.digits = deque(decode_digit(c) for c in val)
        else:
            carry = 0
            while val > 0:
                min_digit = val % 5 + carry
                if min_digit > 2:
                    carry = 1
                    min_digit -= 5
                else:
                    carry = 0
                self.digits.appendleft(min_digit)
                val //= 5

    def to_decimal(self) -> int:
        val = 0
        for digit in self.digits:
            val *= 5
            val += digit
        return val

    def to_string(self) -> str:
        return "".join(encode_digit(digit) for digit in self.digits)


def part1(inp: TextIO) -> int:
    res = sum(SnafuCodedInt(line.rstrip()).to_decimal() for line in inp)
    print(SnafuCodedInt(res).to_string())
    return res
