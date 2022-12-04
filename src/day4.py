from dataclasses import dataclass
from typing import Generator, TextIO, Tuple


@dataclass
class Range:
    lower: int
    upper: int

    @property
    def size(self) -> int:
        return self.upper - self.lower


def parse_range(s: str) -> Range:
    ls, us = s.split("-")
    return Range(int(ls), int(us))


def get_pairs(inp: TextIO) -> Generator[Tuple[Range, Range], None, None]:
    for line in inp:
        line = line.rstrip()

        r1s, r2s = line.split(",")
        yield (parse_range(r1s), parse_range(r2s))


def totally_overlap(p1: Range, p2: Range) -> bool:
    smaller, larger = sorted((p1, p2), key=lambda r: r.size)

    return larger.lower <= smaller.lower and smaller.upper <= larger.upper


def part1(inp: TextIO) -> int:
    return sum(int(totally_overlap(p1, p2)) for p1, p2 in get_pairs(inp))


def partially_overlap(p1: Range, p2: Range) -> bool:
    rlower, rupper = sorted((p1, p2), key=lambda r: r.lower)

    return rlower.upper >= rupper.lower


def part2(inp: TextIO) -> int:
    return sum(int(partially_overlap(p1, p2)) for p1, p2 in get_pairs(inp))
