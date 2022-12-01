import heapq
from typing import Generator, TextIO


def gen_elf_totals(inp: TextIO) -> Generator[int, None, None]:
    this_elf_total = 0
    for line in inp:
        if line := line.rstrip():
            this_elf_total += int(line)
        else:
            yield this_elf_total
            this_elf_total = 0


def part1(inp: TextIO) -> int:
    return max(gen_elf_totals(inp))


def part2(inp: TextIO) -> int:
    return sum(heapq.nlargest(3, gen_elf_totals(inp)))
