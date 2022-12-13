from dataclasses import dataclass
from enum import Enum, auto
from itertools import zip_longest
from typing import Generator, TextIO


class Order(Enum):
    LESS = auto()
    EQUAL = auto()
    GREATER = auto()


@dataclass
class Packet:
    data: int | list["Packet"]

    def compare(self, other: "Packet") -> Order:
        if isinstance(self.data, int) and isinstance(other.data, int):
            return int_compare(self.data, other.data)
        elif isinstance(self.data, list) and isinstance(other.data, list):
            return list_compare(self.data, other.data)
        elif isinstance(self.data, int):
            assert isinstance(other.data, list)
            return list_compare([Packet(self.data)], other.data)
        else:
            assert isinstance(other.data, int)
            return list_compare(self.data, [Packet(other.data)])


def int_compare(lhs: int, rhs: int) -> Order:
    if lhs < rhs:
        return Order.LESS
    elif lhs > rhs:
        return Order.GREATER
    else:
        return Order.EQUAL


def list_compare(lhs: list["Packet"], rhs: list["Packet"]) -> Order:
    for (l_item, r_item) in zip_longest(lhs, rhs, fillvalue=None):
        if l_item is None:
            return Order.LESS
        elif r_item is None:
            return Order.GREATER

        item_result = l_item.compare(r_item)
        if item_result == Order.EQUAL:
            continue
        else:
            return item_result

    return Order.EQUAL


def parse_packet(s: str) -> Packet:
    parse_stack: list[list[Packet]] = []
    i = 0
    while i < len(s):
        if s[i] == ",":
            i += 1
        elif s[i] == "[":
            parse_stack.append([])
            i += 1
        elif s[i] == "]":
            last = parse_stack.pop()
            if not parse_stack:
                return Packet(last)
            else:
                parse_stack[-1].append(Packet(last))
            i += 1
        else:
            j = 0
            for j, c in enumerate(s[i:]):
                if not c.isdigit():
                    break
            parse_stack[-1].append(Packet(int(s[i : i + j])))
            i += j

    raise ValueError


def gen_pairs(inp: TextIO) -> Generator[tuple[Packet, Packet], None, None]:
    while line1 := inp.readline():
        line2 = inp.readline()
        inp.readline()
        yield (parse_packet(line1.rstrip()), parse_packet(line2.rstrip()))


def part1(inp: TextIO) -> int:
    return sum(
        i
        for i, (lhs, rhs) in enumerate(gen_pairs(inp), start=1)
        if lhs.compare(rhs) == Order.LESS
    )


def gen_packets(inp: TextIO) -> Generator[Packet, None, None]:
    for (a, b) in gen_pairs(inp):
        yield a
        yield b


def bubble_insert(packets: list[Packet], p: Packet) -> int:
    "inserts p into the sorted list, maintaining the sort order. Returns the index of p"
    i = len(packets)
    packets.append(p)
    while i > 0 and p.compare((tmp := packets[i - 1])) == Order.LESS:
        packets[i - 1] = p
        packets[i] = tmp
        i -= 1

    return i


def part2(inp: TextIO) -> int:
    packets = []
    for p in gen_packets(inp):
        bubble_insert(packets, p)

    i1 = bubble_insert(packets, Packet([Packet(2)]))
    i2 = bubble_insert(packets, Packet([Packet(6)]))

    return (i1 + 1) * (i2 + 1)
