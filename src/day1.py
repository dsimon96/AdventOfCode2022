import click
import sys
from common import common_options
from typing import TextIO


def do_part1(inp: TextIO) -> int:
    max_elf_total = 0
    this_elf_total = 0
    for line in inp:
        line = line.rstrip()
        if line:
            this_elf_total += int(line)
        else:
            max_elf_total = max(max_elf_total, this_elf_total)
            this_elf_total = 0

    return max_elf_total


@click.command()
@common_options
def day1(part: int):
    if part == 1:
        print(do_part1(sys.stdin))
