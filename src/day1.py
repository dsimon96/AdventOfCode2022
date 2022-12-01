import heapq
import sys
from typing import Generator, TextIO

import click

from common import common_options


def gen_elf_totals(inp: TextIO) -> Generator[int, None, None]:
    this_elf_total = 0
    for line in inp:
        line = line.rstrip()
        if line:
            this_elf_total += int(line)
        else:
            yield this_elf_total
            this_elf_total = 0


def do_part1(inp: TextIO) -> int:
    return max(gen_elf_totals(inp))


def do_part2(inp: TextIO) -> int:
    heap = []
    for elf_total in gen_elf_totals(inp):
        if len(heap) < 3:
            heapq.heappush(heap, elf_total)
        else:
            heapq.heappushpop(heap, elf_total)

    return sum(heap)


@click.command()
@common_options
def day1(part: int):
    if part == 1:
        print(do_part1(sys.stdin))
    else:
        print(do_part2(sys.stdin))
