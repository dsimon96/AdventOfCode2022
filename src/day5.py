from collections import deque
from dataclasses import dataclass
from typing import Callable, Deque, Generator, List, TextIO

Stacks = List[Deque[str]]


@dataclass
class Move:
    n: int
    src: int
    dest: int


def get_init(inp: TextIO) -> Stacks:
    stacks: Stacks = []
    for line in inp:
        if not (line := line.rstrip()):
            break
        i = 0
        while (starti := line.find("[", i)) >= 0:
            stacki = starti // 4
            while stacki >= len(stacks):
                stacks.append(deque())

            stacks[stacki].appendleft(line[starti + 1])
            i = starti + 4

    return stacks


def get_moves(inp: TextIO) -> Generator[Move, None, None]:
    for line in inp:
        tokens = line.split()
        yield Move(n=int(tokens[1]), src=int(tokens[3]), dest=int(tokens[5]))


DoMoveFunc = Callable[[Stacks, Move], None]


def do_sol(inp: TextIO, do_move_fn: DoMoveFunc) -> int:
    stacks = get_init(inp)
    for move in get_moves(inp):
        do_move_fn(stacks, move)

    res = ""
    for stack in stacks:
        res += stack.pop()

    print(res)

    return 0


def part1_do_move(stacks: Stacks, move: Move) -> None:
    srci = move.src - 1
    desti = move.dest - 1
    for _ in range(move.n):
        stacks[desti].append(stacks[srci].pop())


def part1(inp: TextIO) -> int:
    return do_sol(inp, part1_do_move)


def part2_do_move(stacks: Stacks, move: Move) -> None:
    srci = move.src - 1
    desti = move.dest - 1
    tmp: List[str] = []
    for _ in range(move.n):
        tmp.append(stacks[srci].pop())

    while tmp:
        stacks[desti].append(tmp.pop())


def part2(inp: TextIO) -> int:
    return do_sol(inp, part2_do_move)
