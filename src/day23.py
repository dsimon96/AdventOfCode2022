from collections import Counter, deque
from typing import Iterable, Optional, Sequence, TextIO

Vec2 = complex


N = complex(0, -1)
NW = complex(-1, -1)
NE = complex(1, -1)
W = complex(-1, 0)
E = complex(1, 0)
SW = complex(-1, 1)
S = complex(0, 1)
SE = complex(1, 1)

ALL_DIRECTIONS = (NW, N, NE, W, E, SW, S, SE)


NORTH = (N, NW, NE)
SOUTH = (S, SW, SE)
WEST = (W, NW, SW)
EAST = (E, NE, SE)


INIT_ORDER = (NORTH, SOUTH, WEST, EAST)


def parse_inp(inp: TextIO) -> list[Vec2]:
    res = list[Vec2]()
    for y, line in enumerate(inp):
        for x, c in enumerate(line.rstrip()):
            if c == "#":
                res.append(complex(x, y))
    return res


def propose_next(
    order: Iterable[Sequence[Vec2]], occupied: set[Vec2], pos: Vec2
) -> Optional[Vec2]:
    for dir in ALL_DIRECTIONS:
        if (pos + dir) in occupied:
            break
    else:
        return None

    for check in order:
        for dir in check:
            if (pos + dir) in occupied:
                break
        else:
            return pos + check[0]


def bounding_box_area(elf_pos: Iterable[Vec2]) -> int:
    min_x = min(int(pos.real) for pos in elf_pos)
    max_x = max(int(pos.real) for pos in elf_pos)
    min_y = min(int(pos.imag) for pos in elf_pos)
    max_y = max(int(pos.imag) for pos in elf_pos)

    return (max_x - min_x + 1) * (max_y - min_y + 1)


def sim_elves(elf_pos: list[Vec2], max_rounds: Optional[int]) -> tuple[int, list[Vec2]]:
    order = deque(INIT_ORDER)

    round_num = 1
    while max_rounds is None or round_num <= max_rounds:
        all_pos = set(elf_pos)
        proposals = [propose_next(order, all_pos, elf) for elf in elf_pos]

        proposal_counts = Counter[Vec2]()
        for proposal in proposals:
            if proposal is not None:
                proposal_counts[proposal] += 1

        if len(proposal_counts) == 0:
            break

        new_pos = list[Vec2]()
        for elf, proposal in zip(elf_pos, proposals):
            if proposal is None or proposal_counts[proposal] > 1:
                new_pos.append(elf)
            else:
                new_pos.append(proposal)

        elf_pos = new_pos
        order.rotate(-1)
        round_num += 1

    return round_num, elf_pos


def part1(inp: TextIO) -> int:
    _, elf_pos = sim_elves(parse_inp(inp), 10)

    return bounding_box_area(elf_pos) - len(elf_pos)


def part2(inp: TextIO) -> int:
    rounds, _ = sim_elves(parse_inp(inp), None)
    return rounds
